from django.urls import path
from .views import start_chat, chat_list, chat_detail, send_message, delete_chat
from django.urls import path
from .views import check_new_messages
urlpatterns = [
    path('start_chat/<int:part_id>/<int:seller_id>/', start_chat, name='start_chat'),
    path('chats/', chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', chat_detail, name='chat_detail'),
    path('send_message/<int:chat_id>/', send_message, name='send_message'),
    path('chat/<int:chat_id>/delete/', delete_chat, name='delete_chat'),
    path("check_new_messages/", check_new_messages, name="check_new_messages"),

]

