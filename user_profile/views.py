
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProfileForm, ReviewForm
from .models import Profile, Review, Bookmark
from django.contrib.auth.decorators import login_required
from warehouse.models import Part
from chat.models import Chat
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone

@login_required
def profile(request):
    user = request.user
    edit_mode = request.GET.get('edit') == 'true'

    # Автоматическая конвертация тарифа на "free", если подписка истекла
    if user.profile.subscription_end and user.profile.subscription_end < timezone.now():
        if user.profile.tariff != 'free':
            user.profile.tariff = 'free'
            user.profile.save()

    # Получаем отзывы, закладки, чаты и т.д.
    reviews = Review.objects.filter(user=user).order_by('-created_at')
    given_reviews = user.given_reviews.all()
    bookmarks = user.bookmarks.all()
    bookmarks_count = bookmarks.count()
    chats = Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)

    # Вычисляем оставшиеся дни подписки (если подписка оформлена)
    subscription_notification = None
    if user.profile.subscription_end:
        days_left = (user.profile.subscription_end - timezone.now()).days
        if days_left < 0:
            subscription_notification = "Ваша подписка истекла! Продлите подписку, чтобы продолжить пользоваться платными функциями."
        elif days_left < 7:
            subscription_notification = f"Ваша подписка заканчивается через {days_left} дней. Продлите подписку, чтобы не прерывать работу."

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен.")
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
        'chats': chats,
        'subscription_notification': subscription_notification,
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
            messages.success(request, "Отзыв добавлен.")
            return redirect('profile')
    else:
        form = ReviewForm(reviewer=request.user, user=reviewed_user)
    return render(request, 'user_profile/add_review.html', {'form': form, 'reviewed_user': reviewed_user})

@login_required
def view_reviews(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    reviews = Review.objects.filter(user=user_obj).order_by('-created_at')
    return render(request, 'warehouse/view_reviews.html', {'user': user_obj, 'reviews': reviews})

@login_required
def toggle_bookmark(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, part=part)
    if not created:
        bookmark.delete()
        messages.success(request, f'Запчасть "{part.part_type}" для устройства {part.device} {part.brand} {part.model} удалена из закладок.')
    else:
        messages.success(request, f'Запчасть "{part.part_type}" для устройства {part.device} {part.brand} {part.model} добавлена в закладки.')
    next_page = request.GET.get('next')
    if next_page:
        return redirect(next_page)
    return redirect('part_detail', part_id=part.id)

@login_required
def bookmarks(request):
    user_bookmarks = Bookmark.objects.filter(user=request.user).select_related('part')
    return render(request, 'user_profile/bookmarks.html', {'bookmarks': user_bookmarks})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, reviewer=request.user)
    review.delete()
    messages.success(request, "Отзыв был успешно удален.")
    return redirect('profile')