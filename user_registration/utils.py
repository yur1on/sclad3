from django.core import signing
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def generate_email_confirmation_token(user):
    token_data = {'user_id': user.id}
    token = signing.dumps(token_data)
    return token

def verify_email_confirmation_token(token):
    try:
        data = signing.loads(token, max_age=60*60*24)  # Токен действителен 1 день
        return data
    except signing.BadSignature:
        return None

def send_confirmation_email(request, user):
    token = generate_email_confirmation_token(user)
    confirm_url = request.build_absolute_uri(reverse('confirm_email', args=[token]))
    subject = 'Подтверждение регистрации'
    message = (
        f'Здравствуйте, {user.username}!\n\n'
        f'Чтобы подтвердить регистрацию, перейдите по следующей ссылке:\n'
        f'{confirm_url}\n\n'
        f'Если вы не регистрировались на нашем сайте, проигнорируйте это сообщение.'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email])
