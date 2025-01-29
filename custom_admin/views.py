from django.shortcuts import render, get_object_or_404
from warehouse.models import Part
from user_profile.models import Profile, Review
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

@user_passes_test(lambda u: u.is_staff)
def dashboard(request):
    parts_count = Part.objects.count()
    users_count = User.objects.count()
    reviews_count = Review.objects.count()
    return render(request, 'custom_admin/dashboard.html', {
        'parts_count': parts_count,
        'users_count': users_count,
        'reviews_count': reviews_count,
    })

def parts_list(request):
    parts = Part.objects.all()
    return render(request, 'custom_admin/parts_list.html', {'parts': parts})

def users_list(request):
    users = Profile.objects.all()
    return render(request, 'custom_admin/users_list.html', {'users': users})

def reviews_list(request):
    reviews = Review.objects.all()
    return render(request, 'custom_admin/reviews_list.html', {'reviews': reviews})

from django.shortcuts import get_object_or_404, render, redirect
from user_profile.models import Review
from user_profile.forms import ReviewForm  # Если у вас есть форма для редактирования отзыва

def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:reviews_list')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'custom_admin/edit_review.html', {'form': form, 'review': review})


from django.shortcuts import redirect
from user_profile.models import Review

def delete_review(request, id):
    review = Review.objects.get(id=id)
    review.delete()
    return redirect('reviews_list')  # Redirect to your reviews list page


# custom_admin/views.py
from django.shortcuts import render, redirect
from .forms import DataEditForm
from .utils import load_data_from_json, save_data_to_json

def edit_data_view(request):
    data = load_data_from_json()  # Загружаем текущие данные из data.json
    if request.method == 'POST':
        form = DataEditForm(request.POST)
        if form.is_valid():
            # Обрабатываем изменения данных
            new_data = form.cleaned_data
            save_data_to_json(new_data)  # Сохраняем обновленные данные в JSON
            return redirect('success_url')  # Или на другую страницу
    else:
        form = DataEditForm(initial=data)

    return render(request, 'custom_admin/edit_data.html', {'form': form})
