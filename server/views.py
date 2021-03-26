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

