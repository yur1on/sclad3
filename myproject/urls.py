from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from errors import views as errors_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user_profile.urls')),
    path('', include('warehouse.urls')),
    path('user/', include('user_registration.urls')),
    path('admin-panel/', include('custom_admin.urls')),
    path('chat/', include('chat.urls')),
    path("custom-admin/", include("custom_admin.urls")),
    path('notifications/', include('notifications.urls')),
    path('payments/', include('payments.urls', namespace='payments')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



handler404 = errors_views.custom_page_not_found_view
handler500 = errors_views.custom_error_view
handler403 = errors_views.custom_permission_denied_view
handler400 = errors_views.custom_bad_request_view
