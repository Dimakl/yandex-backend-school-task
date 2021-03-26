from django.db import models
from django.contrib.postgres.fields import ArrayField

from server.utils import parse_date_pair


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
        working_hours_start = []
        working_hours_finish = []
        for time in request['working_hours']:
            time_pair = parse_date_pair(time)
            working_hours_start.append(time_pair[0])
            working_hours_finish.append(time_pair[1])
        Courier(id=request['courier_id'], type=request['courier_type'], regions=request['regions'],
                working_hours_start=working_hours_start, working_hours_finish=working_hours_finish,
                current_order_ids=[], completed_order_ids=[]).save()


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
    assign_time = models.CharField(max_length=30, help_text="Время присвоения заказа в формате строки, дабы хранить "
                                                            "сотые доли секунды. В формате RFC 3339.")
    delivered_time = models.CharField(max_length=30, help_text="Время доставки заказа в формате строки, дабы хранить "
                                                               "сотые доли секунды. В формате RFC 3339.")
