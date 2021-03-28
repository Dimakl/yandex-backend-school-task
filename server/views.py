from django.http import HttpResponseBadRequest, HttpResponse
from server.models import *
from server.schemas import validate_schema
import server.schemas as schemas
from server.utils import *


def couriers_post_request(request):
    if request.method != 'POST':
        return
    body = get_request_body_in_json(request)
    errors = validate_schema(body, schemas.couriers_post_request)
    default_errors = PostRequestHelper.check_for_default_post_request_errors(body, errors, Courier, 'courier')
    if default_errors is not None:
        return HttpResponseBadRequest(default_errors)
    created_ids = []
    for courier in body['data']:
        created_ids.append(courier['courier_id'])
        Courier.create_from_request(courier)
    return HttpResponse(json.dumps(PostRequestHelper.create_id_list_object(created_ids, 'courier')))


def redirect_courier_request(request, courier_id):
    if request.method == 'GET':
        return couriers_get_request(request, courier_id)
    if request.method == 'PATCH':
        return couriers_patch_request(request, courier_id)


def couriers_get_request(request, courier_id):
    if courier_id not in Courier.get_unique_ids():
        return HttpResponseBadRequest(
            json.dumps({'errors_description': [f'Courier id {courier_id} is not in database']}))
    courier = Courier.objects.get(id=courier_id)
    return HttpResponse(json.dumps(courier.get_full_info()))


def couriers_patch_request(request, courier_id):
    """
    Принимает от 0-3 полей курьера. (0 - тоже валидное значение!)
    """
    body = get_request_body_in_json(request)
    errors = validate_schema(body, schemas.courier_patch_request)
    if len(errors) != 0:
        return HttpResponseBadRequest(json.dumps({'errors_description': get_string_error_list(errors)}))
    if courier_id not in Courier.get_unique_ids():
        return HttpResponseBadRequest(
            json.dumps({'errors_description': [f'Courier id {courier_id} is not in database']}))
    courier = Courier.change_and_receive_courier_data(courier_id, body)
    return HttpResponse(json.dumps(courier.get_basic_info()))


def orders_post_request(request):
    if request.method != 'POST':
        return
    body = get_request_body_in_json(request)
    errors = validate_schema(body, schemas.orders_post_request)
    default_errors = PostRequestHelper.check_for_default_post_request_errors(body, errors, Order, 'order')
    if default_errors is not None:
        return HttpResponseBadRequest(default_errors)
    failed_ids = []
    for order in body['data']:
        if not Order.weight_is_valid(order['weight']):
            failed_ids.append(order['order_id'])
    if len(failed_ids) != 0:
        return HttpResponseBadRequest(PostRequestHelper.process_weight_errors(failed_ids))
    created_ids = []
    for order in body['data']:
        created_ids.append(order['order_id'])
        Order.create_from_request(order)
    return HttpResponse(json.dumps(PostRequestHelper.create_id_list_object(created_ids, 'order')))


def orders_assign_request(request):
    if request.method != 'POST':
        return
    body = get_request_body_in_json(request)
    errors = validate_schema(body, schemas.orders_assign_post_request)
    if len(errors) != 0:
        return PostRequestHelper.process_parse_response_error(body, errors, 'courier')
    if body['courier_id'] not in Courier.get_unique_ids():
        return HttpResponseBadRequest(json.dumps(
            {'errors_description': f'{body["courier_id"]}: this courier id does not exist in database'}))
    assigned_orders = Courier.assign_orders(body['courier_id'])
    return HttpResponse(json.dumps(assigned_orders))


def orders_complete_request(request):
    if request.method != 'POST':
        return
    body = get_request_body_in_json(request)
    errors = validate_schema(body, schemas.orders_complete_post_request)
    if len(errors) != 0:
        return HttpResponseBadRequest(json.dumps({'errors_description': get_string_error_list(errors)}))
    if body['courier_id'] not in Courier.get_unique_ids():
        return HttpResponseBadRequest(json.dumps(
            {'errors_description': f'{body["courier_id"]}: this courier id does not exist in database'}))
    courier = Courier.objects.get(id=body['courier_id'])
    # Следующая проверка нужна для выполнения идемпотентности:
    if body['order_id'] in courier.completed_order_ids:
        return HttpResponse(json.dumps({'order_id': body['order_id']}))
    if body['order_id'] not in courier.current_order_ids:
        return HttpResponseBadRequest(json.dumps(
            {'errors_description': f'{body["order_id"]}: order with this id is '
                                   f'not assigned to courier with id {body["courier_id"]}'}))
    courier.complete_order(body['order_id'], body['complete_time'])
    return HttpResponse(json.dumps({'order_id': body['order_id']}))