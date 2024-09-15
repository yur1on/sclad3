
from .forms import ProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User, Review
from .forms import ReviewForm
@login_required
def profile(request):
    edit_mode = request.GET.get('edit') == 'true'

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, 'user_profile/profile.html', {'form': form, 'edit_mode': edit_mode})



@login_required
def add_review(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, reviewer=request.user, user=user)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.user = user
            review.save()
            return redirect('profile')  # Перенаправляем на профиль после успешного отзыва
    else:
        form = ReviewForm(reviewer=request.user, user=user)

    return render(request, 'user_profile/add_review.html', {'form': form, 'user': user})


@login_required
def view_reviews(request, user_id):
    user = get_object_or_404(User, id=user_id)
    reviews = Review.objects.filter(user=user).order_by('-created_at')
    return render(request, 'warehouse/view_reviews.html', {'user': user, 'reviews': reviews})


