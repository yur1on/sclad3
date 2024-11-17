

from django.contrib.auth import logout

from .models import Part, PartImage
from .forms import PartForm, PartImageFormSet
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from itertools import groupby
from operator import itemgetter
from django.http import HttpResponse
import openpyxl
from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth.decorators import login_required



def home(request):
    return render(request, 'warehouse/home.html')

from django.core.paginator import Paginator

@login_required
def warehouse_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    query = request.GET.get('q')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    part_type = request.GET.get('part_type')

    # Фильтруем запчасти по пользователю
    parts = Part.objects.filter(user=request.user)

    # Фильтрация по устройству
    if query:
        parts = parts.filter(device__icontains=query)

    # Фильтрация по бренду
    if brand:
        parts = parts.filter(brand__icontains=brand)

    # Фильтрация по модели
    if model:
        parts = parts.filter(model__icontains=model)

    # Фильтрация по типу запчасти
    if part_type:
        parts = parts.filter(part_type__icontains=part_type)

    # Упорядочиваем объекты (например, по дате создания или названию устройства)
    parts = parts.order_by('device', 'brand')  # Замените на подходящие вам поля

    # Пагинация: 30 запчастей на странице
    paginator = Paginator(parts, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Получаем уникальные устройства и бренды для отображения кнопок
    devices = Part.objects.filter(user=request.user).values_list('device', flat=True).distinct().order_by()
    brands = Part.objects.filter(user=request.user).values_list('brand', flat=True).distinct().order_by()

    return render(request, 'warehouse/warehouse.html', {
        'page_obj': page_obj,
        'query': query,
        'brand': brand,
        'model': model,
        'part_type': part_type,
        'devices': devices,
        'brands': brands
    })



@login_required
def add_part(request):
    if request.method == 'POST':
        form = PartForm(request.POST, request.FILES)
        formset = PartImageFormSet(request.POST, request.FILES, queryset=PartImage.objects.none())

        if form.is_valid() and formset.is_valid():
            device = form.cleaned_data.get('device')
            brand = form.cleaned_data.get('brand')
            model = form.cleaned_data.get('model')
            part_type = form.cleaned_data.get('part_type')

            existing_part = Part.objects.filter(
                user=request.user,
                device=device,
                brand=brand,
                model=model,
                part_type=part_type
            ).first()

            if existing_part and 'confirm_add' in request.POST:
                new_part = form.save(commit=False)
                new_part.user = request.user
                new_part.save()

                for image_form in formset:
                    if image_form.cleaned_data:
                        image = image_form.save(commit=False)
                        image.part = new_part
                        image.save()

                messages.success(request, 'Запчасть успешно добавлена повторно!')
                return render(request, 'warehouse/success.html')  # Страница успеха

            if existing_part:
                return render(request, 'warehouse/confirm_add_part.html', {
                    'form': form,
                    'formset': formset,
                    'existing_part': existing_part
                })

            part = form.save(commit=False)
            part.user = request.user
            part.save()

            for image_form in formset:
                if image_form.cleaned_data:
                    image = image_form.save(commit=False)
                    image.part = part
                    image.save()

            messages.success(request, 'Запчасть успешно добавлена!')
            return render(request, 'warehouse/success.html')  # Страница успеха

    else:
        form = PartForm()
        formset = PartImageFormSet(queryset=PartImage.objects.none())

    return render(request, 'warehouse/add_part.html', {'form': form, 'formset': formset})



def logout_view(request):
    logout(request)
    return redirect('home')  # Перенаправление на главную страницу после выхода




from django.core.paginator import Paginator
from django.db.models import Q

def search(request):
    query = request.GET.get('q')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    part_type = request.GET.get('part_type')
    city = request.GET.get('city')

    results = Part.objects.all().order_by('-created_at')

    # Если запрос существует, обрабатываем его
    if query:
        query = query.strip()  # Убираем лишние пробелы
        keywords = query.split()  # Разбиваем строку на слова

        # Создаем пустой Q объект для объединения условий
        q_objects = Q()
        for keyword in keywords:
            # Объединяем условия с помощью AND
            q_objects &= (Q(device__icontains=keyword) |
                          Q(brand__icontains=keyword) |
                          Q(model__icontains=keyword) |
                          Q(part_type__icontains=keyword))

        # Применяем фильтрацию
        results = results.filter(q_objects)

    # Расширенный поиск
    if brand:
        results = results.filter(brand__icontains=brand)
    if model:
        results = results.filter(model__icontains=model)
    if part_type:
        results = results.filter(part_type__icontains=part_type)
    if city:
        results = results.filter(user__profile__city__icontains=city)

    # Пагинация: 30 запчастей на страницу
    paginator = Paginator(results, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'warehouse/search.html', {'page_obj': page_obj})



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

    # Обновляем заголовки для отдельных столбцов
    headers = ["Устройство", "Бренд", "Модель", "Тип запчасти", "Цвет", "Количество (шт.)", "Цена (руб.)"]
    ws.append(headers)

    # Применяем жирный шрифт к заголовкам
    header_font = Font(bold=True)
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font

    # Цвета для заливки (чередуем два цвета для лучшей читабельности)
    fill_colors = ['DCE6F1', 'FCE4D6']  # Светло-синий и светло-оранжевый
    color_index = 0  # Индекс для чередования цветов

    # Получаем данные из модели, сортируем по устройству, бренду, модели и типу запчасти
    parts = Part.objects.filter(user=request.user).order_by('device', 'brand', 'model', 'part_type')

    # Группируем запчасти по комбинации устройства, бренда и модели
    parts_list = list(parts.values('device', 'brand', 'model', 'part_type', 'color', 'quantity', 'price'))
    grouped_parts = groupby(parts_list, key=itemgetter('device', 'brand', 'model'))

    row_num = 2  # Начинаем со второй строки, так как первая — заголовки
    for (device, brand, model), part_group in grouped_parts:
        # Цвет заливки для каждой новой модели
        fill = PatternFill(start_color=fill_colors[color_index], end_color=fill_colors[color_index], fill_type="solid")
        color_index = (color_index + 1) % len(fill_colors)  # Переключаем цвет для следующей модели

        # Добавляем строку с данными устройства, бренда и модели
        ws.append([device, brand, model, "", "", "", ""])
        for col_num in range(1, 8):  # Применяем цвет ко всей строке
            ws.cell(row=row_num, column=col_num).fill = fill

        # Полужирный шрифт для строки устройства, бренда и модели
        ws.cell(row=row_num, column=1).font = Font(bold=True)
        ws.cell(row=row_num, column=2).font = Font(bold=True)
        ws.cell(row=row_num, column=3).font = Font(bold=True)
        row_num += 1

        # Добавляем запчасти для каждой модели
        for part in part_group:
            ws.append([
                "",  # Пустая ячейка для устройства
                "",  # Пустая ячейка для бренда
                "",  # Пустая ячейка для модели
                part['part_type'],
                part['color'] or "Не указан",
                part['quantity'],  # Количество запчастей
                part['price']  # Цена запчастей
            ])
            # Применяем заливку цветом для строк, относящихся к одной модели
            for col_num in range(1, 8):
                ws.cell(row=row_num, column=col_num).fill = fill

            # Форматируем столбец "Количество (шт.)"
            quantity_cell = ws.cell(row=row_num, column=6)
            quantity_cell.number_format = '#,##0 "шт."'  # Форматирование количества с текстом "шт."

            # Форматируем столбец "Цена (руб.)"
            price_cell = ws.cell(row=row_num, column=7)
            price_cell.number_format = '#,##0 "руб."'  # Форматирование числа с текстом "руб."

            row_num += 1

    # Настройка ширины столбцов в зависимости от самого длинного значения в столбце
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Получаем букву столбца
        for cell in col:
            try:
                if cell.value:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            except:
                pass
        adjusted_width = (max_length + 2)  # Добавляем небольшой запас к ширине
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
    model = request.GET.get('model')  # Добавлено
    part_type = request.GET.get('part_type')  # Добавлено

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







from django.shortcuts import render, get_object_or_404
from .models import Part


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Part

@login_required
def part_detail(request, part_id):
    part = get_object_or_404(Part, id=part_id)

    # Проверяем, есть ли эта запчасть в закладках у текущего пользователя
    is_bookmarked = request.user.bookmarks.filter(part=part).exists()

    return render(request, 'warehouse/part_detail.html', {
        'part': part,
        'is_bookmarked': is_bookmarked
    })



@login_required
def user_parts(request, user_id):
    user = get_object_or_404(User, id=user_id)
    parts = Part.objects.filter(user=user)  # Получаем все запчасти этого пользователя

    return render(request, 'warehouse/user_parts.html', {
        'user': user,
        'parts': parts
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




def add_image(request):
    if request.method == 'POST':
        part_id = request.POST.get('part_id')
        images = request.FILES.getlist('image')

        part = get_object_or_404(Part, id=part_id)

        if part.images.count() + len(images) > 5:
            return JsonResponse({'status': 'error', 'message': 'Максимальное количество изображений — 5.'})

        image_responses = []
        for image in images:
            part_image = PartImage(part=part, image=image)  # Adjust according to your image model
            part_image.save()
            image_responses.append({
                'id': part_image.id,
                'url': part_image.image.url,  # Adjust according to your image field
            })

        return JsonResponse({'status': 'success', 'images': image_responses})
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса.'})



def get_brands(request):
    device = request.GET.get('device')
    brands = Part.objects.filter(device=device).values_list('brand', flat=True).distinct()
    return JsonResponse({'brands': list(brands)})


@login_required
def get_devices(request):
    # Фильтруем и сортируем устройства по текущему пользователю
    devices = Part.objects.filter(user=request.user).values_list('device', flat=True).distinct().order_by('device')
    return JsonResponse({'devices': list(devices)})


@login_required
def get_brands(request):
    device = request.GET.get('device')
    # Фильтруем и сортируем бренды по устройству и пользователю
    brands = Part.objects.filter(user=request.user, device=device).values_list('brand', flat=True).distinct().order_by('brand')
    return JsonResponse({'brands': list(brands)})


@login_required
def get_models(request):
    device = request.GET.get('device')
    brand = request.GET.get('brand')
    # Фильтруем и сортируем модели по устройству, бренду и пользователю
    models = Part.objects.filter(user=request.user, device=device, brand=brand).values_list('model', flat=True).distinct().order_by('model')
    return JsonResponse({'models': list(models)})


@login_required
def get_part_types(request):
    device = request.GET.get('device')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    # Фильтруем и сортируем типы запчастей по устройству, бренду, модели и пользователю
    part_types = Part.objects.filter(user=request.user, device=device, brand=brand, model=model).values_list('part_type', flat=True).distinct().order_by('part_type')
    return JsonResponse({'part_types': list(part_types)})


from django.http import JsonResponse
from .models import Part
from django.contrib.auth.decorators import login_required

@login_required
def get_parts(request):
    device = request.GET.get('device')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    part_type = request.GET.get('part_type')

    # Фильтруем запчасти на основе переданных параметров
    parts = Part.objects.filter(user=request.user)

    if device:
        parts = parts.filter(device=device)
    if brand:
        parts = parts.filter(brand=brand)
    if model:
        parts = parts.filter(model=model)
    if part_type:
        parts = parts.filter(part_type=part_type)

    # Формируем данные для ответа с добавлением note и condition
    parts_data = [{
        'id': part.id,
        'device': part.device,
        'brand': part.brand,
        'model': part.model,
        'part_type': part.part_type,
        'color': part.color,
        'quantity': part.quantity,
        'price': part.price,
        'note': part.note,  # Добавлено поле note
        'condition': part.condition,  # Добавлено поле condition
        'images': [{'image_url': image.image.url} for image in part.images.all()]
    } for part in parts]

    return JsonResponse({'parts': parts_data})



@login_required
def import_excel(request):
    if request.method == 'POST':
        file = request.FILES.get('file')

        # Проверяем, является ли файл формата .xlsx
        if not file.name.endswith('.xlsx'):
            messages.error(request, 'Неверный формат файла. Пожалуйста, загрузите файл Excel с расширением .xlsx.')
            return redirect('import_excel')

        try:
            wb = openpyxl.load_workbook(file)
            ws = wb.active

            current_device = None
            current_brand = None
            current_model = None

            for row in ws.iter_rows(min_row=2, values_only=True):  # Пропускаем заголовок
                device, brand, model, part_type, color, quantity, price = row

                # Если в строке указаны устройство, бренд, модель, обновляем их
                if device and brand and model:
                    current_device = device
                    current_brand = brand
                    current_model = model

                # Если не указаны устройство, бренд или модель, используем последние известные значения
                if not current_device or not current_brand or not current_model:
                    messages.error(request, 'Ошибка: строка содержит незаполненные поля для устройства, бренда или модели.')
                    continue  # Пропускаем строку с ошибкой

                # Проверяем, чтобы обязательные поля запчасти были заполнены
                if not all([part_type, quantity, price]):
                    messages.error(request, f'Не удалось импортировать строку: некоторые обязательные поля отсутствуют. ({device} {brand} {model})')
                    continue

                # Проверяем, существует ли запчасть с такими же параметрами в базе данных
                existing_part = Part.objects.filter(
                    user=request.user,
                    device=current_device,
                    brand=current_brand,
                    model=current_model,
                    part_type=part_type
                ).exists()

                if existing_part:
                    # Сообщаем, что запчасть уже существует, и не добавляем ее повторно
                    messages.info(request, f'Запчасть {current_device} {current_brand} {current_model} ({part_type}) уже существует в базе.')
                    continue

                # Создаем новую запись о запчасти, если ее нет в базе
                Part.objects.create(
                    user=request.user,
                    device=current_device,
                    brand=current_brand,
                    model=current_model,
                    part_type=part_type,
                    color=color if color else "Не указан",  # Обрабатываем пустой цвет
                    quantity=int(quantity),  # Количество запчастей
                    price=float(price)  # Цена запчастей
                )

            messages.success(request, 'Данные успешно импортированы!')
            return redirect('warehouse')  # Перенаправляем на склад

        except Exception as e:
            messages.error(request, f'Ошибка при импорте данных: {str(e)}')
            return redirect('import_excel')

    return render(request, 'warehouse/import_parts.html')

from django.contrib.auth.models import User
from warehouse.models import Part

def base_view(request):
    # Подсчёт количества пользователей и запчастей
    user_count = User.objects.count()
    part_count = Part.objects.count()

    return render(request, 'warehouse/base.html', {
        'user_count': user_count,
        'part_count': part_count,
    })


