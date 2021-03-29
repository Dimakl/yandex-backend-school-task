#!/bin/sh

python manage.py migrate --no-input

gunicorn --bind 0.0.0.0:8080 --workers 3 yandex_service.wsgi:application 
