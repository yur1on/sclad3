
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from notifications.models import Notification  # Убедись, что модель уведомлений импортирована
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from chat.models import Chat  # Импортируем модель чата

@login_required
def send_notification(request):
    error_message = None

    if request.method == "POST":
        text = request.POST.get("text")

        if len(text) > 255:
            error_message = "Текст уведомления не должен превышать 255 символов."

        elif text:
            users = User.objects.exclude(id=request.user.id).filter(profile__receive_notifications=True)
            for user in users:
                Notification.objects.create(user=user, sender=request.user, text=text)
            return redirect("notifications_list")

    return render(request, "notifications/send_notification.html", {"error_message": error_message})


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-timestamp")
    return render(request, "notifications/notifications_list.html", {"notifications": notifications})

@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    sender_profile = notification.sender.profile  # Получаем профиль отправителя

    context = {
        "notification": notification,
        "sender_name": sender_profile.full_name if sender_profile and sender_profile.full_name else notification.sender.username,
        "sender_phone": sender_profile.phone if sender_profile else "Не указан",
        "sender_workshop": sender_profile.workshop_name if sender_profile and sender_profile.workshop_name else "Не указано",
    }
    return render(request, "notifications/notification_detail.html", context)

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect("notifications_list")



@login_required
def reply_to_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)

    # Проверяем, есть ли уже чат, связанный с этим уведомлением
    chat, created = Chat.objects.get_or_create(
        user1=min(notification.user, notification.sender, key=lambda u: u.id),
        user2=max(notification.user, notification.sender, key=lambda u: u.id),
        part=None,
        related_notification=notification  # Привязываем к уведомлению
    )

    return redirect('chat_detail', chat_id=chat.id)


@login_required
def toggle_notifications(request):
    profile = request.user.profile
    profile.receive_notifications = not profile.receive_notifications
    profile.save()
    return redirect("notifications_list")
