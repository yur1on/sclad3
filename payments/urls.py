from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('notify/', views.payment_notify, name='payment_notify'),
    path('choose/', views.choose_subscription, name='choose_subscription'),

]