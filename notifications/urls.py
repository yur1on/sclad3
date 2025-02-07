from django.urls import path
from .views import send_notification, notifications_list, notification_detail, delete_notification

urlpatterns = [
    path("send/", send_notification, name="send_notification"),
    path("", notifications_list, name="notifications_list"),
    path("<int:notification_id>/", notification_detail, name="notification_detail"),
    path("<int:notification_id>/delete/", delete_notification, name="delete_notification"),
]
