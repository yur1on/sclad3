# custom_admin/utils.py
import json
import os
from django.conf import settings

# Путь к файлу data.json
data_file_path = os.path.join(settings.BASE_DIR, 'custom_admin', 'data.json')

def load_data_from_json():
    """Чтение данных из файла JSON"""
    with open(data_file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_data_to_json(data):
    """Запись данных в файл JSON"""
    with open(data_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
