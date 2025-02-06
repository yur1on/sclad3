from .views import send_notification
from .views import mark_notification_as_read
from django.urls import path
from .views import notification_list, clear_notifications

urlpatterns = [
    path('send/', send_notification, name='send_notification'),
    path('notifications/read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),
    path("notifications/", notification_list, name="notification_list"),
    path("notifications/clear/", clear_notifications, name="clear_notifications"),
]