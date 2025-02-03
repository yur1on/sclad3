from django.shortcuts import render, get_object_or_404, redirect
from warehouse.models import Part
from django.contrib.auth.models import User
from .forms import MessageForm
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Chat, Message
@login_required
def start_chat(request, part_id, seller_id):
    part = get_object_or_404(Part, id=part_id)
    seller = get_object_or_404(User, id=seller_id)

    chat, created = Chat.objects.get_or_create(user1=request.user, user2=seller, part=part)

    return redirect('chat_detail', chat_id=chat.id)

@login_required
def chat_list(request):
    user = request.user
    chats = Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)

    chat_data = []
    for chat in chats:
        unread_count = Message.objects.filter(
            chat=chat, is_read=False
        ).exclude(sender=user).count()
        chat_data.append({
            'chat': chat,
            'unread_count': unread_count
        })

    return render(request, 'chat/chat_list.html', {'chat_data': chat_data})


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user != chat.user1 and request.user != chat.user2:
        return redirect('chat_list')

    messages = chat.messages.all()
    print(f"Загружено {messages.count()} сообщений в чат {chat_id}")  # Отладка

    return render(request, 'chat/chat_detail.html', {'chat': chat, 'messages': messages})

@login_required
def send_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.save()
        else:
            print(form.errors)  # Отладка ошибок формы
    return redirect('chat_detail', chat_id=chat_id)

@login_required
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user == chat.user1 or request.user == chat.user2:
        chat.delete()
    return redirect('chat_list')


@login_required
def check_new_messages(request):
    user = request.user  # Текущий пользователь

    # Находим все чаты, в которых он участвует
    chats = Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)

    # Считаем сообщения, отправленные НЕ пользователем и непрочитанные
    unread_messages = Message.objects.filter(
        chat__in=chats
    ).exclude(sender=user).filter(is_read=False).count()

    return JsonResponse({"new_messages": unread_messages})


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user != chat.user1 and request.user != chat.user2:
        return redirect('chat_list')

    # Помечаем все сообщения как прочитанные
    chat.messages.filter(sender=chat.user1 if request.user == chat.user2 else chat.user2, is_read=False).update(is_read=True)

    messages = chat.messages.all()
    return render(request, 'chat/chat_detail.html', {'chat': chat, 'messages': messages})