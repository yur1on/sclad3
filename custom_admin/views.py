import json
import os
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from .forms import JSONDataForm

# Проверка, является ли пользователь админом
def is_admin(user):
    return user.is_superuser

# Путь к файлу data.json
DATA_FILE_PATH = os.path.join(settings.BASE_DIR, "warehouse", "data.json")

@user_passes_test(is_admin)
def edit_json(request):
    if request.method == "POST":
        form = JSONDataForm(request.POST)
        if form.is_valid():
            with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(form.cleaned_data["json_data"])
            return redirect("custom_admin:edit_json")
    else:
        try:
            with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
                json_content = json.dumps(json.load(f), indent=4, ensure_ascii=False)
        except (FileNotFoundError, json.JSONDecodeError):
            json_content = "{}"

        form = JSONDataForm(initial={"json_data": json_content})

    return render(request, "custom_admin/edit_json.html", {"form": form})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from user_profile.models import Review

# Проверка, является ли пользователь админом
def is_admin(user):
    return user.is_superuser

# Просмотр всех комментариев
@user_passes_test(is_admin)
def review_list(request):
    reviews = Review.objects.all().select_related("user")  # Загружаем все комментарии с пользователями
    return render(request, "custom_admin/review_list.html", {"reviews": reviews})

# Удаление комментария
@user_passes_test(is_admin)
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect("custom_admin:review_list")


from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

# Проверка, является ли пользователь админом
def is_admin(user):
    return user.is_superuser

# Панель администратора
@user_passes_test(is_admin)
def admin_panel(request):
    return render(request, "custom_admin/admin_panel.html")


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from user_profile.models import Profile  # Учитывая, что профиль хранится в user_profile.models.Profile

# Проверка, является ли пользователь админом
def is_admin(user):
    return user.is_superuser

# Управление пользователями
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.select_related("profile").all()
    return render(request, "custom_admin/user_list.html", {"users": users})

# Удаление пользователя
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect("custom_admin:user_list")


from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from chat.models import Chat

# Панель администрирования чатов
@user_passes_test(is_admin)
def chat_list(request):
    chats = Chat.objects.all().select_related('user1', 'user2').prefetch_related('messages')  # Предзагружаем сообщения
    return render(request, "custom_admin/chat_list.html", {"chats": chats})
