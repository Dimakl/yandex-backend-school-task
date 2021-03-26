from jsonschema import Draft7Validator


def validate_schema(request, schema):
    validator = Draft7Validator(schema)
    return sorted(validator.iter_errors(request), key=lambda e: e.path)


def get_string_error_list(errors):
    error_list = []
    for error in errors:
        error_list.append(error.message + ''.join([f' in object {path}'for path in list(error.path)]))
    return error_list


# Schemas, converted from openapi.yaml:
couriers_post_request = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
      "data": {
        "type": "array",
        "items": {
          "type": "object",
          "additionalProperties": False,
          "properties": {
            "courier_id": {
              "type": "integer"
            },
            "courier_type": {
              "type": "string",
              "enum": [
                "foot",
                "bike",
                "car"
              ]
            },
            "regions": {
              "type": "array",
              "items": {
                "type": "integer"
              }
            },
            "working_hours": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          },
          "required": [
            "courier_id",
            "courier_type",
            "regions",
            "working_hours"
          ]
        }
      }
    },
    "required": [
      "data"
    ]
}

courier_patch_request = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
      "courier_type": {
        "type": "string",
        "enum": [
          "foot",
          "bike",
          "car"
        ]
      },
      "regions": {
        "type": "array",
        "items": {
          "type": "integer"
        }
      },
      "working_hours": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    }
}

orders_post_request = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
      "data": {
        "type": "array",
        "items": {
          "type": "object",
          "additionalProperties": False,
          "properties": {
            "order_id": {
              "type": "integer"
            },
            "weight": {
              "type": "number"
            },
            "region": {
              "type": "integer"
            },
            "delivery_hours": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          },
          "required": [
            "order_id",
            "weight",
            "region",
            "delivery_hours"
          ]
        }
      }
    },
    "required": [
      "data"
    ]
}

orders_assign_post_request = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
      "courier_id": {
        "type": "integer"
      }
    },
    "required": [
      "courier_id"
    ]
}

orders_complete_post_request = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
      "courier_id": {
        "type": "integer"
      },
      "order_id": {
        "type": "integer"
      },
      "complete_time": {
        "type": "string",
        "example": "2021-01-10T10:33:01.42Z"
      }
    },
    "required": [
      "courier_id",
      "order_id",
      "complete_time"
    ]
}
