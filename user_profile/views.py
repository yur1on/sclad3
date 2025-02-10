
from .forms import ProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Review
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from warehouse.models import Part
from .models import Bookmark  # Импортируем модель закладок
from chat.models import Chat
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import Review
@login_required
def profile(request):
    user = request.user
    edit_mode = request.GET.get('edit') == 'true'

    # Получаем отзывы, оставленные пользователю
    reviews = Review.objects.filter(user=user).order_by('-created_at')
    given_reviews = user.given_reviews.all()  # Отзывы, оставленные пользователем

    # Получаем закладки текущего пользователя и их количество
    bookmarks = user.bookmarks.all()
    bookmarks_count = bookmarks.count()

    # Получаем чаты пользователя
    chats = Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user.profile)

    return render(request, 'user_profile/profile.html', {
        'form': form,
        'edit_mode': edit_mode,
        'reviews': reviews,
        'given_reviews': given_reviews,
        'bookmarks': bookmarks,
        'bookmarks_count': bookmarks_count,
        'chats': chats,  # Добавляем чаты в контекст
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


@login_required
def delete_review(request, review_id):
    # Получаем отзыв по ID
    review = get_object_or_404(Review, id=review_id, reviewer=request.user)

    # Удаляем отзыв
    review.delete()

    # Показываем сообщение об успешном удалении
    messages.success(request, "Отзыв был успешно удален.")

    # Перенаправляем обратно на страницу профиля
    return redirect('profile')
