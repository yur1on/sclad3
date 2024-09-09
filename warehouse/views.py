
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.shortcuts import render, redirect
from .forms import PartForm
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import JsonResponse
from .models import Part
from django.contrib.auth.decorators import login_required
def home(request):
    return render(request, 'warehouse/home.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'warehouse/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('warehouse')
    return render(request, 'warehouse/login.html')


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

    return render(request, 'warehouse/warehouse.html', {
        'parts': parts,
        'query': query,
        'brand': brand,
        'model': model,
        'part_type': part_type,
        'devices': devices,  # Добавляем список устройств
        'brands': brands      # Добавляем список брендов
    })


@login_required
def add_part(request):
    if request.method == "POST":
        form = PartForm(request.POST, request.FILES)
        if form.is_valid():
            part = form.save(commit=False)
            part.user = request.user
            part.save()
            return redirect('warehouse')
    else:
        form = PartForm()
    return render(request, 'warehouse/add_part.html', {'form': form})




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
    color = request.GET.get('color')  # Добавлен цвет
    city = request.GET.get('city')

    results = Part.objects.all()

    if query:
        results = results.filter(device__icontains=query)
    if brand:
        results = results.filter(brand__icontains=brand)
    if model:
        results = results.filter(model__icontains=model)
    if part_type:
        results = results.filter(part_type__icontains=part_type)
    if color:
        results = results.filter(color__icontains=color)  # Фильтрация по цвету
    if city:
        results = results.filter(user__profile__city__icontains=city)

    return render(request, 'warehouse/search.html', {'results': results})



@login_required
def edit_part(request, part_id):
    part = get_object_or_404(Part, id=part_id, user=request.user)
    if request.method == 'POST':
        form = PartForm(request.POST, request.FILES, instance=part)
        if form.is_valid():
            form.save()
            return redirect('warehouse')
    else:
        form = PartForm(instance=part)
    return render(request, 'warehouse/edit_part.html', {'form': form})


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





import openpyxl
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Part

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
