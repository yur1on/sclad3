from .views import logout_view
from .views import add_part, get_dynamic_data
from . import views
from .views import add_image
from .views import import_excel
from django.urls import path
from .views import get_regions_and_cities

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
    path('add-part/success/', views.add_part_success, name='add_part_success'),
    path('delete-image/<int:image_id>/', views.delete_image, name='delete_image'),
    path('get-devices/', views.get_devices, name='get_devices'),
    path('get-brands/', views.get_brands, name='get_brands'),
    path('get-models/', views.get_models, name='get_models'),
    path('get-part-types/', views.get_part_types, name='get_part_types'),
    path('get-parts/', views.get_parts, name='get_parts'),
    path('import-excel/', import_excel, name='import_parts'),
    path('', views.base_view, name='home'),
    path('user/<int:user_id>/parts/', views.user_parts, name='user_parts'),
    path('user_parts2/<int:user_id>/', views.user_parts, {'template_name': 'warehouse/user_parts2.html'}, name='user_parts2'),
    path('add-part/', add_part, name='add_part'),
    path('get_dynamic_data/', get_dynamic_data, name='get_dynamic_data'),
    path('get_regions_and_cities/', get_regions_and_cities, name='get_regions_and_cities'),

]












