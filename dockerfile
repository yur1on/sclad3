# Базовый образ Python
FROM python:3.10-slim

# Установим рабочую директорию
WORKDIR /app

# Скопируем requirements.txt и установим зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем все файлы проекта
COPY . /app/

# Открываем порт для доступа
EXPOSE 8000

# Команда запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
