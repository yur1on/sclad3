from django.contrib import messages
from .forms import NotificationForm
from warehouse.models import Part
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def send_notification(request):
    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.user = request.user
            notification.save()
            messages.success(request, "Уведомление отправлено!")
            return redirect('search')
    else:
        form = NotificationForm()
    return render(request, 'notifications/send_notification.html', {'form': form})

def notifications(request):
    if request.user.is_authenticated:
        return {'notifications': Notification.objects.filter(user=request.user, is_read=False)}
    return {}

@login_required
def search_parts(request):
    query = request.GET.get('q', '')
    parts = Part.objects.filter(model__icontains=query)

    if not parts.exists() and query:
        Notification.objects.create(
            user=request.user,
            message=f"Пользователь {request.user.username} ищет запчасть: {query}"
        )

    return render(request, 'warehouse/search_results.html', {'parts': parts})

@csrf_exempt
def mark_notification_as_read(request, notification_id):
    """Удаляет уведомление"""
    if request.method == "POST":
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.delete()
            return JsonResponse({"success": True})
        except Notification.DoesNotExist:
            return JsonResponse({"error": "Уведомление не найдено"}, status=404)
    return JsonResponse({"error": "Неверный запрос"}, status=400)

@login_required
def notification_list(request):
    """Отображает все уведомления и помечает их прочитанными"""
    notifications = Notification.objects.filter(user=request.user)
    notifications.update(is_read=True)  # Отмечаем как прочитанные
    return render(request, "notifications/notifications.html", {"notifications": notifications})

@login_required
def clear_notifications(request):
    """Очищает все уведомления пользователя"""
    if request.method == "POST":
        Notification.objects.filter(user=request.user).delete()
    return redirect("notification_list")
