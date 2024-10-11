from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('add_review/<int:user_id>/', views.add_review, name='add_review'),
    path('user/<int:user_id>/reviews/', views.view_reviews, name='view_reviews'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('toggle-bookmark/<int:part_id>/', views.toggle_bookmark, name='toggle_bookmark'),
]
