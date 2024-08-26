from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegisterForm, PartForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render
from .models import Part
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

def warehouse_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    parts = Part.objects.filter(user=request.user)
    return render(request, 'warehouse/warehouse.html', {'parts': parts})

def add_part(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        form = PartForm(request.POST)
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



def search(request):
    query = request.GET.get('q')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    part_type = request.GET.get('part_type')
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
    if city:
        results = results.filter(user__profile__city__icontains=city)  # Добавлен фильтр по городу

    return render(request, 'warehouse/search.html', {'results': results})
