from django import forms
import json
from django import forms
from django.contrib.auth.models import User
class JSONDataForm(forms.Form):
    json_data = forms.CharField(widget=forms.Textarea, required=True)

    def clean_json_data(self):
        data = self.cleaned_data["json_data"]
        try:
            json.loads(data)  # Проверка, корректный ли JSON
        except json.JSONDecodeError:
            raise forms.ValidationError("Некорректный JSON")
        return data



TARIFF_CHOICES = (
    ('free', 'Бесплатный'),
    ('lite', 'Базовый'),
    ('standard', 'Стандартный'),
    ('standard2', 'Продвинутый'),
    ('standard3', 'Профессиональный'),
    ('premium', 'Неограниченный'),
)

class SubscriptionForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Пользователь")
    tariff = forms.ChoiceField(choices=TARIFF_CHOICES, label="Тариф")
    duration = forms.IntegerField(min_value=1, label="Длительность подписки (в периодах по 30 дней)")
