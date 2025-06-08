
from django.db.models import Value, IntegerField, F
from django.db.models.functions import Lower, Replace
from django.db.models import Case, When, Q
import re
from django.contrib.auth import logout
from pathlib import Path
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from django.http import HttpResponse
from itertools import groupby
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, OuterRef, Subquery
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PartForm, PartImageFormSet
from .models import Part, PartImage
from tariff.utils import check_parts_limit, check_image_limit
from .utils import compress_image
from warehouse.utils import add_watermark_to_image
import os
from django.conf import settings



def home(request):
    return render(request, 'warehouse/home.html')


@login_required
def warehouse_view(request):
    query = request.GET.get('q', '').strip()
    brand = request.GET.get('brand', '')
    model = request.GET.get('model', '')
    part_type = request.GET.get('part_type', '')

    # Базовый фильтр по пользователю
    parts = Part.objects.filter(user=request.user)

    # Список типов запчастей
    known_part_types = [
        'дисплей', 'аккумулятор', 'Вибромотор', 'Датчик', 'приближения', 'полифонический', 'музыкальный', 'Buzzer',
        'слуховой', 'speaker', 'основная', 'фронтальная', 'Катушка', 'беспроводной', 'зарядки', 'Коннектор', 'АКБ', 'дисплея',
        'межплатный', 'Крышка', 'задняя',  'Пластина', 'прижимная', 'зарядки', 'Плата', 'SUB', 'системная', 'Разъем', 'гарнитуры', 'зарядки', 'Рама', 'Рамка', 'дисплея', 'Резинка', 'датчика', 'приближения', 'Сетка', 'Сеточка', 'динамика',
        'Сим-лоток', 'Сим', 'Лоток', 'Сим-считыватель', 'считыватель', 'Сканер', 'отпечатка', 'сенсорный', 'оптический', 'отпечаток', 'Стекло', 'камеры', 'для', 'переклейки', 'Тачскрин', 'Микросхема', 'Микрофон', 'Шлейф', 'антенна', 'Wi-Fi', 'беспроводной', 'зарядка',
        'боковых', 'кнопок',  'кнопка', 'вспышки', 'вспышка', 'дисплея', 'межплатный', 'сканера', 'NFC', 'камера',
        'корпус', 'динамик', 'микрофон',
        'материнская плата', 'шлейф', 'стекло', 'модуль', 'экран', 'зарядное устройство'
    ]

    # Список брендов
    known_brands = [
        'xiaomi', 'samsung', 'apple', 'huawei', 'honor', 'oppo', 'vivo', 'realme',
        'nokia', 'lg', 'sony', 'asus', 'lenovo', 'meizu', 'tecno', 'infinix', 'oppo',
        'TCL', 'Google', 'OnePlus', 'Alcatel', 'Amigoo', 'Archos', 'Asus', 'Black Shark', 'BlackBerry',
        'BLU', 'Cat', 'Caterpillar',  'Coolpad', 'Cubot',  'Doogee', 'Elephone',  'HTC', 'Lenovo',
        'LG', 'Micromax', 'Motorola', 'Nothing',  'Nubia', 'Oukitel',  'Sharp', 'Sony', 'Amazfit',
        'Chuwi', 'Hotwav', 'Teclast', 'UMiDIGI', 'UMiDIGI', 'Garmin', 'Wiko', 'ZTE', 'Poco'
    ]

    def normalize_text(text):
        """Нормализация текста: убираем пробелы и приводим к нижнему регистру."""
        return ''.join(text.split()).lower()

    def split_query(query):
        """Разделение запроса на бренд, модель/номер запчасти и тип запчасти."""
        query_words = query.lower().split()
        brand_words = []
        model_or_part_words = []
        part_type_words = []

        for word in query_words:
            if any(pt.lower() in word.lower() for pt in known_part_types):
                part_type_words.append(word)
            elif any(b.lower() in word.lower() for b in known_brands):
                brand_words.append(word)
            else:
                model_or_part_words.append(word)

        return ' '.join(brand_words).strip(), ' '.join(model_or_part_words).strip(), ' '.join(part_type_words).strip()

    # Обработка поискового запроса
    if query:
        # Разделяем запрос на бренд, модель/номер запчасти и тип запчасти
        brand_query, model_or_part_query, part_type_query = split_query(query)
        normalized_model_query = normalize_text(model_or_part_query) if model_or_part_query else ''
        original_model_query = model_or_part_query.lower() if model_or_part_query else ''
        original_brand_query = brand_query.lower() if brand_query else ''

        # Аннотация для нормализованных полей
        parts = parts.annotate(
            normalized_model=Lower(Replace(F('model'), Value(' '), Value(''))),
            lower_model=Lower(F('model')),
            lower_part_number=Lower(F('part_number')),
            lower_brand=Lower(F('brand'))
        )

        # Фильтрация
        filter_conditions = Q()
        if brand_query and model_or_part_query:
            # Если указаны и бренд, и модель, требуем совпадения обоих
            filter_conditions = (
                Q(lower_brand__icontains=original_brand_query) &
                (Q(normalized_model__icontains=normalized_model_query) |
                 Q(lower_model__icontains=original_model_query) |
                 Q(lower_part_number__icontains=original_model_query))
            )
        elif brand_query:
            # Если указан только бренд
            filter_conditions = Q(lower_brand__icontains=original_brand_query)
        elif model_or_part_query:
            # Если указана только модель или номер запчасти
            filter_conditions = (
                Q(normalized_model__icontains=normalized_model_query) |
                Q(lower_model__icontains=original_model_query) |
                Q(lower_part_number__icontains=original_model_query)
            )

        if filter_conditions:
            parts = parts.filter(filter_conditions)

            # Аннотация для приоритизации
            parts = parts.annotate(
                match_priority=Case(
                    # Точное совпадение модели или номера запчасти
                    When(lower_model=original_model_query, then=Value(3)),
                    When(normalized_model=normalized_model_query, then=Value(3)),
                    When(lower_part_number=original_model_query, then=Value(3)),
                    # Точное совпадение бренда
                    When(lower_brand=original_brand_query, then=Value(2)),
                    # Частичное совпадение модели или номера запчасти
                    When(normalized_model__contains=normalized_model_query, then=Value(2)),
                    When(lower_part_number__contains=original_model_query, then=Value(2)),
                    # Частичное совпадение бренда
                    When(lower_brand__contains=original_brand_query, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
        else:
            parts = parts.annotate(match_priority=Value(0, output_field=IntegerField()))

        # Фильтрация по типу запчасти
        if part_type_query:
            parts = parts.filter(part_type__icontains=part_type_query)
            parts = parts.annotate(
                part_type_match=Case(
                    When(part_type__iexact=part_type_query, then=Value(2)),
                    When(part_type__icontains=part_type_query, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
        else:
            parts = parts.annotate(part_type_match=Value(0, output_field=IntegerField()))
    else:
        # Если запроса нет, все записи имеют нулевой приоритет
        parts = parts.annotate(
            match_priority=Value(0, output_field=IntegerField()),
            part_type_match=Value(0, output_field=IntegerField())
        )

    # Дополнительные фильтры из GET-параметров
    if brand:
        parts = parts.filter(brand__icontains=brand)
    if model:
        parts = parts.filter(model__icontains=model)
    if part_type:
        parts = parts.filter(part_type__icontains=part_type)

    # Сортировка: сначала по совпадению модели/номера/бренда, затем по совпадению типа запчасти, затем по дате
    parts = parts.order_by('-match_priority', '-part_type_match', '-created_at')

    # Пагинация
    total_parts = parts.count()
    paginator = Paginator(parts, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Уникальные устройства и бренды
    devices = Part.objects.filter(user=request.user).values_list('device', flat=True).distinct()
    brands = Part.objects.filter(user=request.user).values_list('brand', flat=True).distinct()

    return render(request, 'warehouse/warehouse.html', {
        'page_obj': page_obj,
        'query': query,
        'brand': brand,
        'model': model,
        'part_type': part_type,
        'devices': devices,
        'brands': brands,
        'total_parts': total_parts,
    })

def logout_view(request):
    logout(request)
    return redirect('home')  # Перенаправление на главную страницу после выхода


def search(request):
    query = request.GET.get('q', '').strip()
    device = request.GET.get('device', '').strip()
    brand = request.GET.get('brand', '').strip()
    model = request.GET.get('model', '').strip()
    part_type = request.GET.get('part_type', '').strip()
    region = request.GET.get('region', '').strip()
    city = request.GET.get('city', '').strip()

    # Исключаем запчасти с количеством 0
    results = Part.objects.filter(quantity__gt=0)

    # Список известных типов запчастей (можно расширить)
    known_part_types = [
        'дисплей', 'аккумулятор', 'Вибромотор', 'Датчик', 'приближения', 'полифонический', 'музыкальный', 'Buzzer',
        'слуховой', 'speaker', 'основная', 'фронтальная', 'Катушка', 'беспроводной', 'зарядки', 'Коннектор', 'АКБ', 'дисплея',
        'межплатный', 'Крышка', 'задняя',  'Пластина', 'прижимная', 'зарядки', 'Плата', 'SUB', 'системная', 'Разъем', 'гарнитуры', 'зарядки', 'Рама', 'Рамка', 'дисплея', 'Резинка', 'датчика', 'приближения', 'Сетка', 'Сеточка', 'динамика',
        'Сим-лоток', 'Сим', 'Лоток', 'Сим-считыватель', 'считыватель', 'Сканер', 'отпечатка', 'сенсорный', 'оптический', 'отпечаток', 'Стекло', 'камеры', 'для', 'переклейки', 'Тачскрин', 'Микросхема', 'Микрофон', 'Шлейф', 'антенна', 'Wi-Fi', 'беспроводной', 'зарядка',
        'боковых', 'кнопок',  'кнопка', 'вспышки', 'вспышка', 'дисплея', 'межплатный', 'сканера', 'NFC', 'камера',
        'корпус', 'динамик', 'микрофон',
        'материнская плата', 'шлейф', 'стекло', 'модуль', 'экран', 'зарядное устройство'
    ]

    # Список известных брендов (можно расширить)
    known_brands = [
        'xiaomi', 'samsung', 'apple', 'huawei', 'honor', 'oppo', 'vivo', 'realme',
        'nokia', 'lg', 'sony', 'asus', 'lenovo', 'meizu', 'tecno', 'infinix', 'oppo',
        'TCL', 'Google', 'OnePlus', 'Alcatel', 'Amigoo', 'Archos', 'Asus', 'Black Shark', 'BlackBerry',
        'BLU', 'Cat', 'Caterpillar',  'Coolpad', 'Cubot',  'Doogee', 'Elephone',  'HTC', 'Lenovo',
        'LG', 'Micromax', 'Motorola', 'Nothing',  'Nubia', 'Oukitel',  'Sharp', 'Sony', 'Amazfit',
        'Chuwi', 'Hotwav', 'Teclast', 'UMiDIGI', 'UMiDIGI', 'Garmin', 'Wiko', 'ZTE', 'Poco'
    ]

    def normalize_text(text):
        """Нормализация текста: убираем пробелы и приводим к нижнему регистру."""
        return ''.join(text.split()).lower()

    def split_query(query):
        """Разделение запроса на бренд, модель/номер запчасти и тип запчасти."""
        query_words = query.lower().split()
        brand_words = []
        model_or_part_words = []
        part_type_words = []

        for word in query_words:
            if any(pt.lower() in word.lower() for pt in known_part_types):
                part_type_words.append(word)
            elif any(b.lower() in word.lower() for b in known_brands):
                brand_words.append(word)
            else:
                model_or_part_words.append(word)

        return ' '.join(brand_words).strip(), ' '.join(model_or_part_words).strip(), ' '.join(part_type_words).strip()

    # Обработка поискового запроса
    if query:
        # Разделяем запрос на бренд, модель/номер запчасти и тип запчасти
        brand_query, model_or_part_query, part_type_query = split_query(query)
        normalized_model_query = normalize_text(model_or_part_query) if model_or_part_query else ''
        original_model_query = model_or_part_query.lower() if model_or_part_query else ''
        original_brand_query = brand_query.lower() if brand_query else ''

        # Аннотация для нормализованных полей
        results = results.annotate(
            normalized_model=Lower(Replace(F('model'), Value(' '), Value(''))),
            lower_model=Lower(F('model')),
            lower_part_number=Lower(F('part_number')),
            lower_brand=Lower(F('brand'))
        )

        # Фильтрация
        filter_conditions = Q()
        if brand_query and model_or_part_query:
            # Если указаны и бренд, и модель, требуем совпадения обоих
            filter_conditions = (
                Q(lower_brand__icontains=original_brand_query) &
                (Q(normalized_model__icontains=normalized_model_query) |
                 Q(lower_model__icontains=original_model_query) |
                 Q(lower_part_number__icontains=original_model_query))
            )
        elif brand_query:
            # Если указан только бренд
            filter_conditions = Q(lower_brand__icontains=original_brand_query)
        elif model_or_part_query:
            # Если указана только модель или номер запчасти
            filter_conditions = (
                Q(normalized_model__icontains=normalized_model_query) |
                Q(lower_model__icontains=original_model_query) |
                Q(lower_part_number__icontains=original_model_query)
            )

        if filter_conditions:
            results = results.filter(filter_conditions)

            # Аннотация для приоритизации
            results = results.annotate(
                match_priority=Case(
                    # Точное совпадение модели или номера запчасти
                    When(lower_model=original_model_query, then=Value(3)),
                    When(normalized_model=normalized_model_query, then=Value(3)),
                    When(lower_part_number=original_model_query, then=Value(3)),
                    # Точное совпадение бренда
                    When(lower_brand=original_brand_query, then=Value(2)),
                    # Частичное совпадение модели или номера запчасти
                    When(normalized_model__contains=normalized_model_query, then=Value(2)),
                    When(lower_part_number__contains=original_model_query, then=Value(2)),
                    # Частичное совпадение бренда
                    When(lower_brand__contains=original_brand_query, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
        else:
            results = results.annotate(match_priority=Value(0, output_field=IntegerField()))

        # Фильтрация по типу запчасти
        if part_type_query:
            results = results.filter(part_type__icontains=part_type_query)
            results = results.annotate(
                part_type_match=Case(
                    When(part_type__iexact=part_type_query, then=Value(2)),
                    When(part_type__icontains=part_type_query, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
        else:
            results = results.annotate(part_type_match=Value(0, output_field=IntegerField()))
    else:
        # Если запроса нет, все записи имеют нулевой приоритет
        results = results.annotate(
            match_priority=Value(0, output_field=IntegerField()),
            part_type_match=Value(0, output_field=IntegerField())
        )

    # Остальные фильтры
    if device:
        results = results.filter(device__icontains=device)
    if brand:
        results = results.filter(brand__icontains=brand)
    if model:
        results = results.filter(model__icontains=model)
    if part_type:
        results = results.filter(part_type__icontains=part_type)
    if region:
        results = results.filter(user__profile__region__icontains=region)
    if city:
        results = results.filter(user__profile__city__icontains=city)

    # Ограничения по подписке
    now = timezone.now()
    active_paid = Q(user__profile__tariff__in=[
        'lite', 'standard', 'standard2', 'standard3', 'premium'
    ]) & Q(user__profile__subscription_end__isnull=False) & Q(user__profile__subscription_end__gte=now)

    # Подзапрос для выбора последних 30 запчастей с количеством > 0
    subquery = Part.objects.filter(user=OuterRef('user_id'), quantity__gt=0).order_by('-created_at').values('pk')[:30]
    results = results.filter(active_paid | Q(pk__in=Subquery(subquery)))

    # Сортировка: сначала по совпадению, затем по дате
    results = results.order_by('-match_priority', '-part_type_match', '-created_at')

    # Пагинация
    paginator = Paginator(results, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'warehouse/search.html', {
        'page_obj': page_obj,
        'query': query,
        'device': device,
        'brand': brand,
        'model': model,
        'part_type': part_type,
        'region': region,
        'city': city,
    })


@login_required
def edit_part(request, part_id):
    part = get_object_or_404(Part, id=part_id)

    if request.method == 'POST':
        # Обновляем поля запчасти
        part.device = request.POST.get('device')
        part.brand = request.POST.get('brand')
        part.model = request.POST.get('model')
        part.part_type = request.POST.get('part_type')
        part.color = request.POST.get('color')
        part.quantity = request.POST.get('quantity')
        part.price = request.POST.get('price')
        part.save()

        # Обрабатываем изображения
        if 'images' in request.FILES:
            images = request.FILES.getlist('images')  # Получаем список загруженных изображений
            for image in images:
                # Проверьте, что не больше 5 изображений
                if part.images.count() < 5:
                    part.images.create(image=image)  # Создаем объект изображения

        return redirect('warehouse')  # Перенаправляем после успешного сохранения

    return render(request, 'warehouse/edit_part.html', {'part': part})


@login_required
def delete_part(request, part_id):
    part = get_object_or_404(Part, id=part_id, user=request.user)
    if request.method == 'POST':
        part.delete()
        return redirect('warehouse')
    return render(request, 'warehouse/delete_part.html', {'part': part})


@login_required(login_url='login')
def profile(request):
    return render(request, 'warehouse/profile.html')


@login_required(login_url='login')
def warehouse(request):
    return render(request, 'warehouse/warehouse.html')




@login_required
def export_excel(request):
    # Создаем новый Excel файл
    wb = Workbook()
    ws = wb.active
    ws.title = "Запчасти"

    # Заголовки столбцов
    headers = ["Устройство", "Бренд", "Модель", "Тип запчасти", "Цвет", "Количество (шт.)", "Цена (руб.)"]
    ws.append(headers)

    # Применяем жирный шрифт к заголовкам
    header_font = Font(bold=True)
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font

    # Получаем данные из модели, сортируем по устройству, бренду и модели
    user_parts = Part.objects.filter(user=request.user).order_by('device', 'brand', 'model')

    # Определяем цвета заливки
    phone_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")  # Светло-голубой
    tablet_fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")  # Светло-зелёный
    watch_fill = PatternFill(start_color="FFFFE0", end_color="FFFFE0", fill_type="solid")   # Светло-жёлтый
    separator_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")  # Светло-серый

    row_num = 2  # Начинаем со второй строки (первая — заголовки)

    # Группируем данные только по устройству
    for device, device_parts in groupby(user_parts, lambda x: x.device):
        # Определяем цвет заливки для столбца "Устройство"
        if device == "Телефон":
            fill = phone_fill
        elif device == "Планшет":
            fill = tablet_fill
        elif device == "Смарт-часы":
            fill = watch_fill
        else:
            fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")  # Белый по умолчанию

        # Записываем все запчасти для текущего устройства
        for part in device_parts:
            ws.append([
                part.device,
                part.brand,
                part.model,
                part.part_type,
                part.color or "Не указан",
                part.quantity,
                part.price
            ])

            # Применяем заливку только к ячейке в столбце "Устройство" (первый столбец)
            device_cell = ws.cell(row=row_num, column=1)
            device_cell.fill = fill

            # Форматируем столбцы "Количество" и "Цена"
            quantity_cell = ws.cell(row=row_num, column=6)
            quantity_cell.number_format = '#,##0 "шт."'
            price_cell = ws.cell(row=row_num, column=7)
            price_cell.number_format = '#,##0 "руб."'

            row_num += 1

        # Добавляем разделительную строку после группы устройств
        for col_num in range(1, 8):
            separator_cell = ws.cell(row=row_num, column=col_num)
            separator_cell.fill = separator_fill
        row_num += 1

    # Настройка ширины столбцов
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[column].width = adjusted_width

    # Создаем HTTP ответ с Excel файлом
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=parts.xlsx'
    wb.save(response)

    return response

@login_required
def get_brands_for_device(request):
    device = request.GET.get('device')
    brands = Part.objects.filter(user=request.user, device=device).values_list('brand', flat=True).distinct()
    return JsonResponse({'brands': list(brands)})


@login_required
def filter_parts(request):
    device = request.GET.get('device')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    part_type = request.GET.get('part_type')

    # Фильтрация запчастей по устройству, бренду, модели и типу
    parts = Part.objects.filter(user=request.user, device=device, brand=brand)
    if model:
        parts = parts.filter(model__icontains=model)
    if part_type:
        parts = parts.filter(part_type__icontains=part_type)

    # Подготовка данных для ответа
    parts_data = [
        {
            'id': part.id,
            'device': part.device,
            'brand': part.brand,
            'model': part.model,
            'part_type': part.part_type,
            'color': part.color,
            'quantity': part.quantity,
            'price': part.price,
            'image': part.image.url if part.image else None
        }
        for part in parts
    ]

    return JsonResponse({'parts': parts_data})


@login_required
def part_detail(request, part_id):
    part = get_object_or_404(Part, id=part_id)

    # Проверяем, есть ли эта запчасть в закладках у текущего пользователя
    is_bookmarked = request.user.bookmarks.filter(part=part).exists()

    return render(request, 'warehouse/part_detail.html', {
        'part': part,
        'is_bookmarked': is_bookmarked
    })




def add_part_success(request):
    return render(request, 'warehouse/add_part_success.html')


def delete_image(request, image_id):
    if request.method == 'POST' and request.user.is_authenticated:
        # Получаем изображение по ID
        image = get_object_or_404(PartImage, id=image_id)

        # Проверяем, принадлежит ли изображение текущему пользователю (если нужно)
        # if image.part.user != request.user:
        #     return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

        # Удаляем изображение
        image.delete()

        # Возвращаем ответ
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def add_image(request):
    if request.method == 'POST':
        part_id = request.POST.get('part_id')
        images = request.FILES.getlist('image')

        part = get_object_or_404(Part, id=part_id)

        if part.images.count() + len(images) > 5:
            return JsonResponse({'status': 'error', 'message': 'Максимальное количество изображений — 5.'})

        image_responses = []
        for image in images:
            compressed = compress_image(image)
            watermarked = add_watermark_to_image(compressed)
            part_image = PartImage(part=part, image=watermarked)
            part_image.save()
            image_responses.append({
                'id': part_image.id,
                'url': part_image.image.url,
            })

        return JsonResponse({'status': 'success', 'images': image_responses})
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса.'})




@login_required
def get_devices(request):
    devices = Part.objects.filter(user=request.user).values_list('device', flat=True).distinct().order_by('device')
    return JsonResponse({'devices': list(devices)})

@login_required
def get_brands(request):
    device = request.GET.get('device')
    brands = Part.objects.filter(user=request.user, device=device).values_list('brand', flat=True).distinct().order_by('brand')
    return JsonResponse({'brands': list(brands)})

@login_required
def get_models(request):
    device = request.GET.get('device')
    brand = request.GET.get('brand')
    models = Part.objects.filter(user=request.user, device=device, brand=brand).values_list('model', flat=True).distinct().order_by('model')
    return JsonResponse({'models': list(models)})

@login_required
def get_part_types(request):
    device = request.GET.get('device')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    part_types = Part.objects.filter(user=request.user, device=device, brand=brand, model=model).values_list('part_type', flat=True).distinct().order_by('part_type')
    return JsonResponse({'part_types': list(part_types)})

@login_required
def get_parts(request):
    device = request.GET.get('device')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    part_type = request.GET.get('part_type')

    filters = {'user': request.user}
    if device:
        filters['device'] = device
    if brand:
        filters['brand'] = brand
    if model:
        filters['model'] = model
    if part_type:
        filters['part_type'] = part_type

    parts = Part.objects.filter(**filters).prefetch_related('images')
    parts_data = [{
        'id': part.id,
        'device': part.device,
        'brand': part.brand,
        'model': part.model,
        'part_type': part.part_type,
        'part_number': part.part_number or '',  # Добавляем part_number
        'color': part.color,
        'quantity': part.quantity,
        'price': str(part.price),  # Преобразуем Decimal в строку для JSON
        'note': part.note,
        'condition': part.condition,
        'images': [{'image_url': image.image.url} for image in part.images.all()]
    } for part in parts]

    return JsonResponse({'parts': parts_data})


def base_view(request):
    # Подсчёт количества пользователей и запчастей
    user_count = User.objects.count()
    part_count = Part.objects.count()

    return render(request, 'warehouse/base.html', {
        'user_count': user_count,
        'part_count': part_count,
    })


# Путь к JSON файлу
# DATA_FILE = Path(__file__).resolve().parent.parent / "json_manager" / "г.json"

DATA_FILE = Path(__file__).resolve().parent / "data.json"

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)


def get_dynamic_data(request):
    """Универсальное представление для динамического обновления данных."""
    data = load_data()  # Загружаем данные из JSON
    device = request.GET.get("device")
    brand = request.GET.get("brand")
    part_type = request.GET.get("part_type")
    response = {}

    if device:
        response["brands"] = data.get(device, {}).get("brands", [])
        response["part_types"] = data.get(device, {}).get("part_types", [])

    if device and brand:
        response["models"] = data.get(device, {}).get("models", {}).get(brand, [])

    if device and part_type:
        response["colors"] = data.get(device, {}).get("colors", {}).get(part_type, [])
        response["conditions"] = data.get(device, {}).get("conditions", [])

    return JsonResponse(response)






# Регистрация pillow-heif для поддержки HEIC-формата
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    # Если библиотека не установлена, HEIC-формат не будет поддерживаться
    pass

@login_required
def add_part(request):
    """Добавление запчасти с обработкой формы и изображений, с учетом тарифных ограничений."""
    profile = getattr(request.user, 'profile', None)
    if not profile or not profile.city or not profile.phone:
        messages.error(request, 'Перед началом создания склада, укажите, пожалуйста, город и номер телефона в вашем профиле.')
        return redirect('profile')

    if request.method == 'POST':
        # Проверка лимита запчастей по тарифу
        if check_parts_limit(request.user):
            tariff = request.user.profile.tariff
            if tariff == 'free':
                error_message = "Вы достигли лимита в 30 запчастей для бесплатного тарифа. Для добавления новых запчастей обновите тариф."
            elif tariff == 'lite':
                error_message = "Вы достигли лимита в 500 запчастей для тарифа Lite. Для добавления новых запчастей обновите тариф."
            elif tariff == 'standard':
                error_message = "Вы достигли лимита в 2000 запчастей для тарифа Стандарт. Для добавления новых запчастей обновите тариф."
            elif tariff == 'standard2':
                error_message = "Вы достигли лимита в 7000 запчастей для тарифа Стандарт 2. Для добавления новых запчастей обновите тариф."
            elif tariff == 'standard3':
                error_message = "Вы достигли лимита в 15000 запчастей для тарифа Стандарт 3. Для добавления новых запчастей обновите тариф."
            else:
                error_message = "Лимит запчастей достигнут."
            messages.error(request, error_message)
            return redirect('profile')

        # Сохранение данных формы и файлов в сессии, если они есть
        if 'form_data' in request.session:
            form_data = request.session.pop('form_data')
            form_files = request.session.pop('form_files', {})
            form = PartForm(form_data, form_files)
            formset = PartImageFormSet(form_data, form_files, queryset=PartImage.objects.none())
        else:
            form = PartForm(request.POST, request.FILES)
            formset = PartImageFormSet(request.POST, request.FILES, queryset=PartImage.objects.none())

        if form.is_valid() and formset.is_valid():
            images = [img_form for img_form in formset if img_form.cleaned_data and img_form.cleaned_data.get('image')]
            if request.user.profile.tariff == 'free' and check_image_limit(request.user, len(images)):
                messages.error(request, "На бесплатном тарифе можно загрузить только 1 изображение для запчасти.")
                return render(request, 'warehouse/add_part.html', {'form': form, 'formset': formset})

            # Обработка данных формы
            part_type = form.cleaned_data['part_type']
            chip_marking = request.POST.get('chip_marking', '').strip()
            if part_type == "Микросхема" and chip_marking:
                form.cleaned_data['part_type'] = f"{part_type} {chip_marking}"

            device = form.cleaned_data['device']
            brand = form.cleaned_data['brand']
            model = form.cleaned_data['model']
            part_type = form.cleaned_data['part_type']
            condition = form.cleaned_data['condition']
            color = form.cleaned_data.get('color')
            if color == '':
                color = None

            # Проверка на существование запчасти с учетом цвета
            existing_part = Part.objects.filter(
                user=request.user,
                device=device,
                brand=brand,
                model=model,
                part_type=part_type,
                condition=condition,
                color=color
            ).first()

            if existing_part and 'confirm_add' in request.POST:
                # Добавление дубликата, если пользователь подтвердил
                new_part = form.save(commit=False)
                new_part.user = request.user
                new_part.save()
                for image_form in formset:
                    if image_form.cleaned_data and image_form.cleaned_data.get('image'):
                        image_obj = image_form.save(commit=False)
                        compressed = compress_image(image_obj.image)
                        watermarked = add_watermark_to_image(compressed)
                        image_obj.image = watermarked
                        image_obj.part = new_part
                        image_obj.save()

                return render(request, 'warehouse/success.html')

            if existing_part:
                # Сохранение данных формы и файлов в сессии
                request.session['form_data'] = request.POST.dict()
                request.session['form_files'] = request.FILES.dict()
                return render(request, 'warehouse/confirm_add_part.html', {
                    'form': form,
                    'formset': formset,
                    'existing_part': existing_part
                })

            # Сохранение новой запчасти
            part = form.save(commit=False)
            part.user = request.user
            part.save()
            for image_form in formset:
                if image_form.cleaned_data and image_form.cleaned_data.get('image'):
                    image_obj = image_form.save(commit=False)
                    compressed = compress_image(image_obj.image)
                    watermarked = add_watermark_to_image(compressed)
                    image_obj.image = watermarked
                    image_obj.part = part
                    image_obj.save()


            return render(request, 'warehouse/success.html', {'message': 'Запчасть успешно добавлена!'})

        else:
            # Отладка ошибок валидации
            messages.error(request, 'Ошибка валидации формы. Проверьте введенные данные.')
            if form.errors:
                messages.error(request, f'Ошибки формы: {form.errors}')
            if formset.errors:
                messages.error(request, f'Ошибки formset: {formset.errors}')
            return render(request, 'warehouse/add_part.html', {'form': form, 'formset': formset})

    else:
        form = PartForm()
        formset = PartImageFormSet(queryset=PartImage.objects.none())

    return render(request, 'warehouse/add_part.html', {'form': form, 'formset': formset})

def get_regions_and_cities(request):
    file_path = os.path.join(settings.BASE_DIR, 'static/json/belarus_regions_and_cities.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return JsonResponse(data)


def user_parts_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_parts = Part.objects.filter(user_id=user_id, quantity__gt=0).order_by('device', 'brand', 'model')

    grouped_parts = {}
    for device, device_parts in groupby(user_parts, lambda x: x.device):
        grouped_parts[device] = {}
        for brand, brand_parts in groupby(device_parts, lambda x: x.brand):
            grouped_parts[device][brand] = list(brand_parts)

    return render(request, 'warehouse/user_parts.html', {
        'grouped_parts': grouped_parts,
        'viewed_user': user,
    })

@login_required
def user_parts(request, user_id, template_name='warehouse/user_parts.html'):
    user = get_object_or_404(User, id=user_id)
    user_parts = Part.objects.filter(user_id=user_id).order_by('device', 'brand', 'model')

    grouped_parts = {}
    for device, device_parts in groupby(user_parts, lambda x: x.device):
        grouped_parts[device] = {}
        for brand, brand_parts in groupby(device_parts, lambda x: x.brand):
            grouped_parts[device][brand] = list(brand_parts)

    return render(request, template_name, {
        'grouped_parts': grouped_parts,
        'viewed_user': user,
        'viewed_user_full_name': user.profile.full_name,
    })




@login_required
def delete_all_parts_page(request):
    if request.method == 'POST':
        user_parts = Part.objects.filter(user=request.user)

        for part in user_parts:
            for image in part.images.all():
                if image.image:  # Проверяем, есть ли файл
                    image_path = os.path.join(settings.MEDIA_ROOT, str(image.image))
                    if os.path.exists(image_path):
                        os.remove(image_path)  # Удаляем файл изображения

                image.delete()  # Удаляем запись из базы

        user_parts.delete()  # Удаляем запчасти

        messages.success(request, 'Все запчасти и их изображения были успешно удалены.')
        return redirect('warehouse')

    return render(request, 'warehouse/delete_all_parts.html')


def about_project(request):
    return render(request, 'warehouse/about_project.html')


def search_user_parts(request, user_id):
    viewed_user = get_object_or_404(User, id=user_id)
    parts = Part.objects.filter(user=viewed_user, quantity__gt=0)

    # Обработка параметров поиска
    query = request.GET.get('query', '').strip()
    if query:
        parts = parts.filter(
            Q(model__icontains=query) |  # Используем поле model
            Q(part_type__icontains=query)
        )

    # Группировка запчастей
    grouped_parts = {}
    for part in parts:
        grouped_parts.setdefault(part.device, {}).setdefault(part.brand, []).append(part)

    return render(request, 'warehouse/user_parts.html', {
        'viewed_user': viewed_user,
        'grouped_parts': grouped_parts,
    })


def user_agreement_view(request):
    return render(request, 'warehouse/user_agreement.html')



def privacy_policy_view(request):
    return render(request, 'warehouse/privacy_policy.html')
