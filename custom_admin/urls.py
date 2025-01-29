
from django.urls import path
from . import views
app_name = 'custom_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('parts/', views.parts_list, name='parts_list'),
    path('users/', views.users_list, name='users_list'),
    path('reviews/', views.reviews_list, name='reviews_list'),
    path('reviews/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete-review/<int:id>/', views.delete_review, name='delete_review'),
    path('edit-data/', views.edit_data_view, name='edit_data'),
]

