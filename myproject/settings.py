
from decouple import config  # Импортируем python-decouple
import os
from pathlib import Path
from dotenv import load_dotenv


# Путь до корня проекта (там, где лежит manage.py и .env)
BASE_DIR = Path(__file__).resolve().parent.parent

# загружаем .env
load_dotenv(BASE_DIR / '.env')

# теперь SECRET_KEY берётся из окружения
SECRET_KEY = os.getenv('SECRET_KEY')

CRISPY_TEMPLATE_PACK = 'bootstrap4'  # Или 'bootstrap5', в зависимости от версии

# Для работы https.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = True  # Перенаправляет HTTP на HTTPS
SESSION_COOKIE_SECURE = True  # Куки только по HTTPS
CSRF_COOKIE_SECURE = True  # CSRF-токены только по HTTPS
SECURE_HSTS_SECONDS = 31536000  # Включает HSTS на год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


DEBUG = False
ALLOWED_HOSTS = ['mobirazbor.by']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django-app-db',
        'USER': 'app_user',
        'PASSWORD': '89U1JKpkBQVTErtpIgfi',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}


# DEBUG = True
# ALLOWED_HOSTS = []
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'sklad_new',
#         'USER': 'yura',
#         'PASSWORD': '',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


LOGIN_URL = 'login'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'warehouse',
    'user_profile',
    'crispy_forms',
    'user_registration',
    'widget_tweaks',
    'custom_admin',
    'chat',
    'notifications',
    'tariff',
    'payments',
    'storages',
    'errors',
    'advertisements',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise для обслуживания статики
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'warehouse.context_processors.counts',
                'notifications.context_processors.unread_notifications',
                'warehouse.context_processors.subscription_status',
                'advertisements.context_processors.active_advertisements',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'



AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Настройки для статических файлов
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGOUT_REDIRECT_URL = '/'

# --------------------------
# S3 Storage Settings для медиафайлов (фото)
# --------------------------
AWS_ACCESS_KEY_ID = "07d847f251ab915a0b94"              # Ваш Access Key ID
AWS_SECRET_ACCESS_KEY = "jplKti1izNopbASzCqdlVR47udlRi8jhKOQG9Udf"  # Ваш Secret Key
AWS_STORAGE_BUCKET_NAME = "parts-images"                 # Имя вашего bucket
AWS_S3_ENDPOINT_URL = "https://s3-minsk-dc2.cloud.mts.by"  # HTTPS-эндпоинт API S3

STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        'OPTIONS': {
            'access_key': AWS_ACCESS_KEY_ID,
            'secret_key': AWS_SECRET_ACCESS_KEY,
            'bucket_name': AWS_STORAGE_BUCKET_NAME,
            'endpoint_url': AWS_S3_ENDPOINT_URL,
            'signature_version': 's3',
        },
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_FILE_OVERWRITE = False

# Формируем MEDIA_URL для доступа к файлам через веб
MEDIA_URL = "https://s3-website-minsk-dc2.cloud.mts.by/parts-images/"



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'mobirazbor@mail.ru'
EMAIL_HOST_PASSWORD = 'j4Cy2rgYCj70K6SWcnU3'
DEFAULT_FROM_EMAIL = 'mobirazbor@mail.ru'
