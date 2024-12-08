
from .forms import ProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Review
from .forms import ReviewForm
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from warehouse.models import Part
from django.contrib import messages
from .models import Bookmark  # Импортируем модель закладок

@login_required
def profile(request):
    edit_mode = request.GET.get('edit') == 'true'

    # Получаем отзывы, оставленные пользователю
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')

    # Получаем закладки текущего пользователя и количество закладок
    bookmarks = request.user.bookmarks.all()
    bookmarks_count = bookmarks.count()  # Подсчитываем количество закладок

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, 'user_profile/profile.html', {
        'form': form,
        'edit_mode': edit_mode,
        'reviews': reviews,  # Передаем отзывы в шаблон
        'bookmarks': bookmarks,  # Передаем закладки в шаблон
        'bookmarks_count': bookmarks_count  # Передаем количество закладок в шаблон
    })




@login_required
def add_review(request, user_id):
    reviewed_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, reviewer=request.user, user=reviewed_user)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.user = reviewed_user
            review.save()
            return redirect('profile')  # Перенаправляем на профиль после успешного отзыва
    else:
        form = ReviewForm(reviewer=request.user, user=reviewed_user)

    return render(request, 'user_profile/add_review.html', {'form': form, 'reviewed_user': reviewed_user})



@login_required
def view_reviews(request, user_id):
    user = get_object_or_404(User, id=user_id)
    reviews = Review.objects.filter(user=user).order_by('-created_at')
    return render(request, 'warehouse/view_reviews.html', {'user': user, 'reviews': reviews})





@login_required
def toggle_bookmark(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, part=part)

    if not created:
        # Если закладка уже существует, удаляем её
        bookmark.delete()
        messages.success(request, f'Запчасть "{part.part_type}" для устройства {part.device} {part.brand} {part.model} удалена из закладок.')
    else:
        messages.success(request, f'Запчасть "{part.part_type}" для устройства {part.device} {part.brand} {part.model} добавлена в закладки.')

    # Проверяем, откуда пришел запрос: из профиля или с деталей запчасти
    next_page = request.GET.get('next')  # Попытаемся получить параметр next из URL
    if next_page:
        return redirect(next_page)  # Если есть next, перенаправляем на указанный путь

    # Если next не указан, перенаправляем на страницу деталей запчасти
    return redirect('part_detail', part_id=part.id)



@login_required
def bookmarks(request):
    user_bookmarks = Bookmark.objects.filter(user=request.user).select_related('part')
    return render(request, 'user_profile/bookmarks.html', {'bookmarks': user_bookmarks})

