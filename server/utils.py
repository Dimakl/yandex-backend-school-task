import datetime as dt
import json

from server.schemas import get_string_error_list


def parse_date_rfc(date_string):
    return dt.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')


def parse_date_pair(date_string):
    d1, d2 = date_string.split('-')
    h1, m1 = [int(x) for x in d1.split(':')]
    h2, m2 = [int(x) for x in d2.split(':')]
    return h1 * 60 + m1, h2 * 60 + m2


def get_request_body_in_json(request):
    return json.loads(request.body.decode('utf8'))


def generate_time_arrays_from_request_hours(hours):
    hours_start = []
    hours_finish = []
    for time in hours:
        time_pair = parse_date_pair(time)
        hours_start.append(time_pair[0])
        hours_finish.append(time_pair[1])
    return hours_start, hours_finish


def generate_request_hours_from_time_arrays(hours_start, hours_finish):
    hours = []
    for i in range(len(hours_start)):
        start = hours_start[i]
        finish = hours_finish[i]
        hours.append(f'{start // 60:02d}:{start % 60:02d}-{finish // 60:02d}:{finish % 60:02d}')
    return hours


class CouriersPostRequestHelper:

    @staticmethod
    def process_parse_response_error(body, errors):
        error_list = get_string_error_list(errors)
        error_couriers_id = set()
        if 'data' in body.keys():
            for error in errors:
                path = list(error.path)
                if len(path) != 2:
                    continue
                if 'courier_id' in body['data'][path[1]]:
                    error_couriers_id.add(body['data'][path[1]]['courier_id'])
        response = {
            'validation_error': CouriersPostRequestHelper.create_courier_list_object(list(error_couriers_id)),
            'errors_description': error_list
        }
        return json.dumps(response)

    @staticmethod
    def create_courier_list_object(error_couriers_id):
        return {'couriers': [{'id': x} for x in error_couriers_id]}

    @staticmethod
    def process_ununique_ids_error(failed_ids):
        errors_description = []
        validation_error = CouriersPostRequestHelper.create_courier_list_object(failed_ids)
        for f_id in failed_ids:
            errors_description.append(f"Courier id {f_id} is already in database")
        response = {
            'validation_error': validation_error,
            'errors_description': errors_description
        }
        return json.dumps(response)
