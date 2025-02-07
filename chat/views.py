
from .forms import MessageForm
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render
from .models import Chat, Message
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Chat
from django.contrib.auth.models import User

@login_required
def start_chat(request, seller_id, part_id=None):
    seller = get_object_or_404(User, id=seller_id)

    if part_id:
        from warehouse.models import Part  # Импортируем здесь, чтобы избежать циклического импорта
        part = get_object_or_404(Part, id=part_id)
        chat, created = Chat.objects.get_or_create(user1=request.user, user2=seller, part=part)
    else:
        chat, created = Chat.objects.get_or_create(user1=request.user, user2=seller, part=None)

    return redirect('chat_detail', chat_id=chat.id)


@login_required
def chat_list(request):
    user = request.user
    chats = Chat.objects.filter(Q(user1=user) | Q(user2=user))

    chat_data = []
    for chat in chats:
        if user in chat.hidden_for.all():
            has_new_messages = Message.objects.filter(chat=chat, is_read=False).exclude(sender=user).exists()
            if has_new_messages:
                chat.hidden_for.remove(user)  # Показываем чат, если есть новые сообщения
            else:
                continue  # Пропускаем скрытый чат, если нет новых сообщений

        unread_count = Message.objects.filter(chat=chat, is_read=False).exclude(sender=user).count()
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

    if request.user in [chat.user1, chat.user2]:
        chat.hidden_for.add(request.user)  # Скрываем чат для пользователя

        # Если оба скрыли чат — удаляем его полностью
        if chat.hidden_for.count() == 2:
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