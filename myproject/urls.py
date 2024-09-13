from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('warehouse.urls')),
    path('', include('user_profile.urls')),
    path('', include('warehouse.urls')),
    path('user/', include('user_registration.urls')),  # Добавьте эту строку
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

