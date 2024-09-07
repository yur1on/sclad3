from .views import logout_view
from . import views
from django.urls import path


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('search/', views.search, name='search'),
    path('warehouse/', views.warehouse_view, name='warehouse'),
    path('add-part/', views.add_part, name='add_part'),
    path('edit-part/<int:part_id>/', views.edit_part, name='edit_part'),
    path('delete-part/<int:part_id>/', views.delete_part, name='delete_part'),
    path('logout/', logout_view, name='logout'),
    path('export_excel/', views.export_excel, name='export_excel'),
]






