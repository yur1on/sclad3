#!/bin/bash

echo "Ждем БД"

sleep 10

echo "Применяем миграции"
python ./manage.py makemigrations
python ./manage.py migrate

echo "Запускаемся"
python ./manage.py runserver 0.0.0.0:8000
