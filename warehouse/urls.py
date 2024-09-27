from .views import logout_view
from . import views
from django.urls import path
from .views import add_image
urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('warehouse/', views.warehouse_view, name='warehouse'),
    path('add-part/', views.add_part, name='add_part'),
    path('edit-part/<int:part_id>/', views.edit_part, name='edit_part'),
    path('delete-part/<int:part_id>/', views.delete_part, name='delete_part'),
    path('logout/', logout_view, name='logout'),
    path('export_excel/', views.export_excel, name='export_excel'),
    path('filter_parts/', views.filter_parts, name='filter_parts'),
    path('part/<int:part_id>/', views.part_detail, name='part_detail'),
    path('add-image/', add_image, name='add_image'),


    # Новый URL для страницы успеха
    path('add-part/success/', views.add_part_success, name='add_part_success'),
    path('delete-image/<int:image_id>/', views.delete_image, name='delete_image'),
    path('get-devices/', views.get_devices, name='get_devices'),
    path('get-brands/', views.get_brands, name='get_brands'),
    path('get-models/', views.get_models, name='get_models'),
    path('get-part-types/', views.get_part_types, name='get_part_types'),
    path('get-parts/', views.get_parts, name='get_parts'),

]












