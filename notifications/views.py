from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.contrib.auth.models import User

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.contrib.auth.models import User

@login_required
def send_notification(request):
    error_message = None  # Переменная для ошибки

    if request.method == "POST":
        text = request.POST.get("text")

        if len(text) > 255:
            error_message = "Текст уведомления не должен превышать 255 символов."

        elif text:
            users = User.objects.exclude(id=request.user.id)
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
    notification.is_read = True  # Отмечаем как прочитанное
    notification.save()
    return render(request, "notifications/notification_detail.html", {"notification": notification})

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect("notifications_list")
