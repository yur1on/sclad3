
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from .models import PartImage
from .forms import PartForm, PartImageFormSet  # Добавляем форму для изображений
from django.shortcuts import render, get_object_or_404
import openpyxl
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Part, PartImage  # Adjust according to your actual models

from django.shortcuts import get_object_or_404
from .models import PartImage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import PartImage
def home(request):
    return render(request, 'warehouse/home.html')


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

    # Получаем уникальные устройства и бренды для отображения кнопок
    devices = Part.objects.filter(user=request.user).values_list('device', flat=True).distinct()
    brands = Part.objects.filter(user=request.user).values_list('brand', flat=True).distinct()

    # Добавляем список URL изображений для каждого запчасти
    for part in parts:
        part.image_urls = [image.image.url for image in part.images.all()]

    return render(request, 'warehouse/warehouse.html', {
        'parts': parts,
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
            part = form.save(commit=False)
            part.user = request.user  # если нужно сохранить пользователя
            part.save()

            for image_form in formset:
                if image_form.cleaned_data:
                    image = image_form.save(commit=False)
                    image.part = part  # присвоить запчасть каждому изображению
                    image.save()

            return redirect('add_part_success')  # Редирект на страницу успеха
    else:
        form = PartForm()
        formset = PartImageFormSet(queryset=PartImage.objects.none())

    return render(request, 'warehouse/add_part.html', {'form': form, 'formset': formset})


def logout_view(request):
    logout(request)
    return redirect('home')  # Перенаправление на главную страницу после выхода



from django.shortcuts import render
from .models import Part

def search(request):
    query = request.GET.get('q')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    part_type = request.GET.get('part_type')
    color = request.GET.get('color')
    city = request.GET.get('city')

    results = Part.objects.all().order_by('-created_at')  # Ordering by creation time

    if query:
        results = results.filter(device__icontains=query)
    if brand:
        results = results.filter(brand__icontains=brand)
    if model:
        results = results.filter(model__icontains=model)
    if part_type:
        results = results.filter(part_type__icontains=part_type)
    if color:
        results = results.filter(color__icontains=color)
    if city:
        results = results.filter(user__profile__city__icontains=city)

    return render(request, 'warehouse/search.html', {'results': results})



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
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Запчасти"

    # Заголовки для таблицы
    ws.append(["Устройство", "Бренд", "Модель", "Тип запчасти", "Цвет", "Количество", "Цена"])

    # Данные из модели, принадлежащие текущему пользователю
    parts = Part.objects.filter(user=request.user).order_by('device', 'brand', 'model')  # Сортировка по устройству, бренду и модели
    for part in parts:
        ws.append([part.device, part.brand, part.model, part.part_type, part.color, part.quantity, part.price])

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




@login_required
def part_detail(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    return render(request, 'warehouse/part_detail.html', {'part': part})



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
