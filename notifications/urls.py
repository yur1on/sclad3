from django.urls import path
from .views import (
    send_notification,
    notifications_list,
    notification_detail,
    delete_notification,
    reply_to_notification,
    toggle_notifications,
    mark_as_read,
)

urlpatterns = [
    path("", notifications_list, name="notifications_list"),  # Оставляем только один маршрут для списка
    path("send/", send_notification, name="send_notification"),
    path("<int:notification_id>/", notification_detail, name="notification_detail"),
    path("<int:notification_id>/delete/", delete_notification, name="delete_notification"),
    path("<int:notification_id>/reply/", reply_to_notification, name="reply_to_notification"),
    path("toggle-notifications/", toggle_notifications, name="toggle_notifications"),
    path("<int:notification_id>/mark_as_read/", mark_as_read, name="mark_as_read"),
]