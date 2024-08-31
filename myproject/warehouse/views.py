
from django.contrib.auth import authenticate, login
from .forms import UserRegisterForm, PartForm
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import Part
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from .forms import PartForm
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

    parts = Part.objects.filter(user=request.user)

    if query:
        parts = parts.filter(device__icontains=query)
    if brand:
        parts = parts.filter(brand__icontains=brand)
    if model:
        parts = parts.filter(model__icontains=model)
    if part_type:
        parts = parts.filter(part_type__icontains=part_type)

    return render(request, 'warehouse/warehouse.html', {
        'parts': parts,
        'query': query,
        'brand': brand,
        'model': model,
        'part_type': part_type
    })


@login_required
def add_part(request):
    if request.method == 'POST':
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


