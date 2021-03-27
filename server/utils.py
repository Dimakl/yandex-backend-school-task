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


class PostRequestHelper:

    @staticmethod
    def process_parse_response_error(body, errors, entity_name):
        error_list = get_string_error_list(errors)
        error_entities_id = set()
        if 'data' in body.keys():
            for error in errors:
                path = list(error.path)
                if len(path) != 2:
                    continue
                if f'{entity_name}_id' in body['data'][path[1]]:
                    error_entities_id.add(body['data'][path[1]][f'{entity_name}_id'])
        response = {
            'validation_error': PostRequestHelper.create_id_list_object(list(error_entities_id), entity_name),
            'errors_description': error_list
        }
        return json.dumps(response)

    @staticmethod
    def create_id_list_object(error_id, entity_name):
        return {entity_name: [{'id': x} for x in error_id]}

    @staticmethod
    def process_ununique_ids_error(failed_ids, entity_name):
        errors_description = []
        validation_error = PostRequestHelper.create_id_list_object(failed_ids, entity_name)
        for f_id in failed_ids:
            errors_description.append(f"{f_id}: this {entity_name} id  is already in database")
        response = {
            'validation_error': validation_error,
            'errors_description': errors_description
        }
        return json.dumps(response)

    @staticmethod
    def process_weight_errors(failed_ids):
        """
        Здесь практически дублицируется код из process_ununique_ids_error, но их совмещение
        приведет к некоторой путаннице, так что я решил разделить их.
        """
        errors_description = []
        validation_error = PostRequestHelper.create_id_list_object(failed_ids, 'order')
        for f_id in failed_ids:
            errors_description.append(f"{f_id}: weight of order with this id is bigger than 50 or less than 0.01")
        response = {
            'validation_error': validation_error,
            'errors_description': errors_description
        }
        return json.dumps(response)

    @staticmethod
    def check_for_default_post_request_errors(body, errors, entity_class, entity_name):
        if len(errors) != 0:
            return PostRequestHelper.process_parse_response_error(body, errors, entity_name)
        ids = set(entity_class.get_unique_ids())
        failed_ids = []
        for order in body['data']:
            if order[f'{entity_name}_id'] in ids:
                failed_ids.append(order[f'{entity_name}_id'])
        if len(failed_ids) != 0:
            return PostRequestHelper.process_ununique_ids_error(failed_ids, entity_name)
        return None
