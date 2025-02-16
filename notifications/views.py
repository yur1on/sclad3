
from chat.models import Chat
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Notification

@login_required
def send_notification(request):
    error_message = None

    if request.method == "POST":
        text = request.POST.get("text")
        if len(text) > 255:
            error_message = "Текст уведомления не должен превышать 255 символов."
        elif text:
            # Генерируем общий идентификатор для уведомления
            broadcast_id = uuid.uuid4()

            # Создаем копию для себя: отправитель = получатель, и помечаем как прочитанное
            Notification.objects.create(
                user=request.user,
                sender=request.user,
                text=text,
                is_read=True,  # чтобы не учитывалось в счетчике
                broadcast_id=broadcast_id
            )

            # Создаем уведомления для остальных пользователей
            users = User.objects.exclude(id=request.user.id).filter(profile__receive_notifications=True)
            for user in users:
                Notification.objects.create(
                    user=user,
                    sender=request.user,
                    text=text,
                    broadcast_id=broadcast_id
                )
            return redirect("notifications_list")

    return render(request, "notifications/send_notification.html", {"error_message": error_message})


@login_required
def notifications_list(request):
    received_notifications = Notification.objects.filter(user=request.user).exclude(sender=request.user).order_by("-timestamp")
    sent_notifications = Notification.objects.filter(user=request.user, sender=request.user).order_by("-timestamp")
    return render(request, "notifications/notifications_list.html", {
        "received_notifications": received_notifications,
        "sent_notifications": sent_notifications,
    })


@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    # Разрешаем просмотр, если пользователь является получателем или отправителем
    if request.user != notification.user and request.user != notification.sender:
        raise Http404("Уведомление не найдено.")

    # Если уведомление для вас (вы его получили)
    if notification.user == request.user and notification.sender != request.user:
        notification.is_read = True
        notification.save()
        sender_profile = notification.sender.profile
        context = {
            "notification": notification,
            "received_notifications": Notification.objects.filter(user=request.user).exclude(sender=request.user).order_by("-timestamp"),
            "sent_notifications": Notification.objects.filter(user=request.user, sender=request.user).order_by("-timestamp"),
            "sender_name": sender_profile.full_name if sender_profile and sender_profile.full_name else notification.sender.username,
            "sender_phone": sender_profile.phone if sender_profile else "Не указан",
            "sender_workshop": sender_profile.workshop_name if sender_profile and sender_profile.workshop_name else "Не указано",
        }
    # Если уведомление – ваша копия (отправленное)
    elif notification.user == request.user and notification.sender == request.user:
        context = {
            "notification": notification,
            "received_notifications": Notification.objects.filter(user=request.user).exclude(sender=request.user).order_by("-timestamp"),
            "sent_notifications": Notification.objects.filter(user=request.user, sender=request.user).order_by("-timestamp"),
        }
    return render(request, "notifications/notifications_list.html", context)


@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    # Проверяем, что текущий пользователь имеет право удалять уведомление
    if request.user != notification.user and request.user != notification.sender:
        raise Http404("Уведомление не найдено.")

    # Если удаляется уведомление, отправленное вами (копия, где вы являетесь отправителем)
    if notification.sender == request.user and notification.user == request.user:
        Notification.objects.filter(broadcast_id=notification.broadcast_id).delete()
    else:
        # Если уведомление получено от другого пользователя – удаляем только его
        notification.delete()

    return redirect("notifications_list")


@login_required
def reply_to_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    chat, created = Chat.objects.get_or_create(
        user1=min(notification.user, notification.sender, key=lambda u: u.id),
        user2=max(notification.user, notification.sender, key=lambda u: u.id),
        part=None,
        related_notification=notification
    )
    return redirect('chat_detail', chat_id=chat.id)


@login_required
def toggle_notifications(request):
    profile = request.user.profile
    profile.receive_notifications = not profile.receive_notifications
    profile.save()
    return redirect("notifications_list")
