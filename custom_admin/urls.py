
from django.urls import path
from .views import admin_panel, edit_json, review_list, delete_review, user_list, delete_user
from django.urls import path
from .views import admin_panel, edit_json, review_list, delete_review, user_list, delete_user, chat_list

app_name = 'custom_admin'

urlpatterns = [

    path("", admin_panel, name="admin_panel"),
    path("edit-json/", edit_json, name="edit_json"),
    path("reviews/", review_list, name="review_list"),
    path("reviews/delete/<int:review_id>/", delete_review, name="delete_review"),
    path("users/", user_list, name="user_list"),
    path("users/delete/<int:user_id>/", delete_user, name="delete_user"),
    path("chats/", chat_list, name="chat_list"),
]

