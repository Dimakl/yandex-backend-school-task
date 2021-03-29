import datetime
import json
from dateutil.parser import *

from server.schemas import get_string_error_list


def parse_date_rfc(date_string):
    return parse(date_string)


def date_to_string(date):
    return date.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()


def parse_date_pair(date_string):
    d1, d2 = date_string.split('-')
    h1, m1 = [int(x) for x in d1.split(':')]
    h2, m2 = [int(x) for x in d2.split(':')]
    return h1 * 60 + m1, h2 * 60 + m2


def get_request_body_in_json(request):
    return json.loads(request.body.decode('utf8'))


def generate_time_arrays_from_request_hours(hours):
    time_array = []
    for time in hours:
        time_array.append(parse_date_pair(time))
    hours_start = []
    hours_finish = []
    for item in sorted(time_array):
        hours_start.append(item[0])
        hours_finish.append(item[1])
    return hours_start, hours_finish


def generate_request_hours_from_time_arrays(hours_start, hours_finish):
    hours = []
    for i in range(len(hours_start)):
        start = hours_start[i]
        finish = hours_finish[i]
        hours.append(f'{start // 60:02d}:{start % 60:02d}-{finish // 60:02d}:{finish % 60:02d}')
    return hours


class KnapsackSolver:

    table = []
    weights = []
    answer = []

    def solve_knapsack(self, max_weight, weights):
        n = len(weights)
        self.weights = weights
        self.table = [[0 for _ in range(max_weight + 1)] for _ in range(n + 1)]
        for i in range(n + 1):
            for j in range(max_weight + 1):
                if j == 0 or i == 0:
                    self.table[i][j] = 0
                elif weights[i - 1] <= j:
                    self.table[i][j] = max(weights[i - 1] + self.table[i - 1][j - weights[i - 1]], self.table[i - 1][j])
                else:
                    self.table[i][j] = self.table[i - 1][j]
        return self.find_ans_knapsack(n, max_weight)

    def find_ans_knapsack(self, k, s):
        if self.table[k][s] == 0:
            return
        if self.table[k - 1][s] == self.table[k][s]:
            self.find_ans_knapsack(k - 1, s)
        else:
            self.find_ans_knapsack(k - 1, s - self.weights[k - 1])
            self.answer.append(k - 1)


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
    def create_id_list_object(ids, entity_name):
        return {entity_name: [{'id': x} for x in ids]}

    @staticmethod
    def process_ununique_ids_error(failed_ids, entity_name):
        errors_description = []
        validation_error = PostRequestHelper.create_id_list_object(failed_ids, entity_name)
        for f_id in failed_ids:
            errors_description.append(f'{f_id}: this {entity_name} id already exists in database')
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
            errors_description.append(f'{f_id}: weight of order with this id is bigger than 50 or less than 0.01')
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
