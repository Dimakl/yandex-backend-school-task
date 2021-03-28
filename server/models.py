from datetime import datetime
from django.db import models
from django.contrib.postgres.fields import ArrayField
from server.utils import generate_time_arrays_from_request_hours, generate_request_hours_from_time_arrays, \
    date_to_string, PostRequestHelper


class Courier(models.Model):
    id = models.IntegerField(primary_key=True, help_text="Id курьера, переданный при его создании, уникален.")
    type = models.CharField(max_length=4, help_text="Тип курьера - из {foot, bike, car}, создавать ChoiceField"
                                                    "было бы излишне, тк при помощи json схем гарантируется что"
                                                    "тип курьера будет требуемым.")
    regions = ArrayField(models.IntegerField(), help_text="Массив регионов, в которые курьер готов отправиться.")
    working_hours_start = ArrayField(models.IntegerField(),
                                     help_text="Список времени начала смены курьера (в минутах от 00:00),"
                                               "использование 2 массивов вместо создания объекта пар показалось "
                                               "более разумным. len(working_hours_start) == len(working_hours_finish).")
    working_hours_finish = ArrayField(models.IntegerField(), help_text="Список времени конца смены курьера,"
                                                                       "(см. working_hours_start)")
    current_order_ids = ArrayField(models.IntegerField(),
                                   help_text="Список id заказов присвоенных курьеру, принадлежность заказа дублируется "
                                             "в самом классе заказа для ускорения быстродействия. Используются id "
                                             "вместо ForeignKey т.к. id - primary key заказа и т.к. в массив в PSQL"
                                             "невозможно добавить ссылки на объекты.")
    completed_order_ids = ArrayField(models.IntegerField(),
                                     help_text="Список id заказов выполненных курьером. Причины выбора такой структуры "
                                               "хранения аналогичны причинам current_order_ids.")

    @staticmethod
    def get_unique_ids():
        return Courier.objects.values_list('id', flat=True)

    @staticmethod
    def create_from_request(request):
        working_hours_start, working_hours_finish = generate_time_arrays_from_request_hours(request['working_hours'])
        Courier(id=request['courier_id'], type=request['courier_type'], regions=request['regions'],
                working_hours_start=working_hours_start, working_hours_finish=working_hours_finish,
                current_order_ids=[], completed_order_ids=[]).save()

    @staticmethod
    def change_and_receive_courier_data(courier_id, request):
        courier = Courier.objects.get(id=courier_id)
        print(request)
        if 'regions' in request:
            courier.regions = request['regions']
        if 'courier_type' in request:
            courier.type = request['courier_type']
        if 'working_hours' in request:
            courier.working_hours_start, courier.working_hours_finish = \
                generate_time_arrays_from_request_hours(request['working_hours'])
        courier.save()
        courier.update_current_orders()
        return courier

    def get_basic_info(self):
        return {'courier_id': self.id,
                'courier_type': self.type,
                'regions': self.regions,
                'working_hours':
                    generate_request_hours_from_time_arrays(self.working_hours_start, self.working_hours_finish)}

    def update_current_orders(self):
        pass

    @staticmethod
    def assign_orders(courier_id):
        courier = Courier.objects.get(id=courier_id)
        assignable_orders = []
        for order in Order.objects.filter(assigned_to_id=-1, region__in=courier.regions):
            # TODO: Add time validation check
            assignable_orders.append(order)
        new_orders = courier.get_assignable_order_list(assignable_orders)
        current_time = date_to_string(datetime.now())
        new_current_orders = courier.current_order_ids
        for order in new_orders:
            print(current_time)

            order.assigned_to_id = courier_id
            order.assign_time = current_time
            new_current_orders.append(order.id)
            order.save()
        courier.current_order_ids = new_current_orders
        courier.save()
        return {'orders': PostRequestHelper.create_id_list_object(courier.current_order_ids, 'orders')['orders'],
                'assign_time': current_time}

    # TODO: add algo for optimal pick
    def get_assignable_order_list(self, orders):
        max_weight = self.get_max_weight() - \
                     sum([Order.objects.get(order_id).weight for order_id in self.current_order_ids])
        picked_orders = []
        for order in orders:
            if max_weight - order.weight >= 0:
                picked_orders.append(order)
                max_weight -= order.weight
        return picked_orders

    def get_max_weight(self):
        return {'foot': 10, 'bike': 15, 'car': 50}[self.type]


class Order(models.Model):
    id = models.IntegerField(primary_key=True, help_text="Id курьера, переданный при его создании, уникален.")
    weight = models.FloatField(help_text="Вес товара: число с плавающей точкой в промежутке [0.01; 50].")
    region = models.IntegerField(help_text="Регион доставки заказа.")
    delivery_hours_start = ArrayField(models.IntegerField(),
                                      help_text="Список времени начала принятия клиентом заказа"
                                                " (извиняюсь за формулировку! :) ) (в минутах от 00:00),"
                                                "аналогичен Courier.working_hours_start.")
    delivery_hours_finish = ArrayField(models.IntegerField(), help_text="Список времени конца принятия клиентом заказа,"
                                                                        "(см. delivery_hours_start)")
    assigned_to_id = models.IntegerField(default=-1, help_text="Id курьера, которому присвоен заказ. Если такого "
                                                               "курьера нет - значение поля = -1.")
    assign_time = models.CharField(max_length=40, help_text="Время присвоения заказа в формате строки, дабы хранить "
                                                            "сотые доли секунды. В формате RFC 3339.")
    delivered_time = models.CharField(max_length=40, help_text="Время доставки заказа в формате строки, дабы хранить "
                                                               "сотые доли секунды. В формате RFC 3339.")

    @staticmethod
    def get_unique_ids():
        return Order.objects.values_list('id', flat=True)

    @staticmethod
    def create_from_request(request):
        delivery_hours_start, delivery_hours_finish = generate_time_arrays_from_request_hours(request['delivery_hours'])
        Order(id=request['order_id'], weight=request['weight'], region=request['region'],
              delivery_hours_start=delivery_hours_start, delivery_hours_finish=delivery_hours_finish, assigned_to_id=-1,
              assign_time="", delivered_time="").save()

    @staticmethod
    def weight_is_valid(weight):
        return 0.01 <= weight <= 50

    def is_time_valid(self, courier):
        if len(self.delivery_hours_start) == 0 or len(courier.working_hours_start) == 0:
            return False
        courier_time_id, order_time_id = 0, 0
        # todo: check code
        while courier_time_id != len(courier.working_hours_start) or \
                order_time_id != len(self.delivery_hours_start):
            if self.delivery_hours_finish[order_time_id] < courier.working_hours_start[courier_time_id]:
                order_time_id += 1
                pass
            if courier.working_hours_finish[courier_time_id] < self.delivery_hours_start[order_time_id]:
                courier_time_id += 1
                pass
            # ?