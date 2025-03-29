from .forms import ProfileForm, ReviewForm
from .models import Profile, Review, Bookmark
from django.contrib.auth.decorators import login_required
from warehouse.models import Part
from chat.models import Chat
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import os
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def profile(request):
    user = request.user
    edit_mode = request.GET.get('edit') == 'true'
    days_since_expiry = None

    # Автоматическая конвертация тарифа и удаление запчастей
    if user.profile.subscription_end and user.profile.subscription_end < timezone.now():
        if user.profile.tariff != 'free':
            user.profile.tariff = 'free'
            user.profile.save()

        days_since_expiry = (timezone.now() - user.profile.subscription_end).days
        if days_since_expiry >= 30:
            parts = Part.objects.filter(user=user).order_by('-created_at')
            if parts.count() > 30:
                # Сохраняем последние 30 запчастей, остальные будем удалять
                parts_to_keep_ids = parts[:30].values_list('id', flat=True)
                parts_to_delete = Part.objects.filter(user=user).exclude(id__in=parts_to_keep_ids)
                for part in parts_to_delete:
                    for image in part.images.all():
                        # Метод delete() в модели PartImage удаляет файл из S3 через django-storages
                        image.delete()
                    part.delete()
                messages.warning(request, "Ваша подписка истекла более 30 дней назад. Все запчасти, кроме последних 30, были удалены.")
        elif days_since_expiry >= 0:
            days_left_until_deletion = 30 - days_since_expiry
            messages.info(request, f"Ваша подписка истекла {days_since_expiry} дней назад. Через {days_left_until_deletion} дней все запчасти, кроме последних 30, будут удалены. Оформите подписку, чтобы сохранить данные.")

    reviews = Review.objects.filter(user=user).order_by('-created_at')
    given_reviews = user.given_reviews.all()
    bookmarks = user.bookmarks.all()
    bookmarks_count = bookmarks.count()
    chats = Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)

    # Используем renew_subscription для кнопки продления
    renew_subscription = False
    if user.profile.subscription_end:
        days_left = (user.profile.subscription_end - timezone.now()).days
        if days_left < 7 and days_left >= 0:
            renew_subscription = True

    subscription_period = None
    if user.profile.subscription_end and user.profile.subscription_end > timezone.now():
        subscription_period = (user.profile.subscription_start, user.profile.subscription_end)

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
        'renew_subscription': renew_subscription,
        'subscription_period': subscription_period,
        'days_since_expiry': days_since_expiry,
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
            if not review.rating:
                review.rating = 5
            review.save()
            messages.success(request, "Отзыв добавлен.")
            return redirect('profile')
    else:
        form = ReviewForm(reviewer=request.user, user=reviewed_user)
        form.initial['rating'] = 5
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
