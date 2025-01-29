from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from custom_admin.views import dashboard
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user_profile.urls')),
    path('', include('warehouse.urls')),
    path('user/', include('user_registration.urls')),
    path('admin-panel/', include('custom_admin.urls')),
    path('admin-panel/', dashboard, name='dashboard'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

