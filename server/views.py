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
    if len(errors) != 0:
        return HttpResponseBadRequest(CouriersPostRequestHelper.process_parse_response_error(body, errors))
    courier_ids = set(Courier.get_unique_ids())
    failed_ids = []
    for courier in body['data']:
        if courier['courier_id'] in courier_ids:
            failed_ids.append(courier['courier_id'])
    if len(failed_ids) != 0:
        return HttpResponseBadRequest(CouriersPostRequestHelper.process_ununique_ids_error(failed_ids))
    created_ids = []
    for courier in body['data']:
        created_ids.append(courier['courier_id'])
        Courier.create_from_request(courier)
    return HttpResponse(json.dumps(CouriersPostRequestHelper.create_courier_list_object(created_ids)))


def redirect_courier_request(request, courier_id):
    if request.method == 'GET':
        return couriers_get_request(request, courier_id)
    if request.method == 'PATCH':
        return couriers_patch_request(request, courier_id)


def couriers_get_request(request, courier_id):
    pass


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


