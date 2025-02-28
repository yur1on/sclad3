from django import forms
from .models import Profile, Review

BELARUS_REGIONS = [
    ('Минская область', 'Минская область'),
    ('Гомельская область', 'Гомельская область'),
    ('Гродненская область', 'Гродненская область'),
    ('Брестская область', 'Брестская область'),
    ('Могилевская область', 'Могилевская область'),
    ('Витебская область', 'Витебская область'),
]

TARIFF_CHOICES = (
    ('free', 'Бесплатный'),
    ('standard', 'Стандарт'),
    ('standard2', 'Стандарт 2'),  # Добавлен новый тариф
    ('premium', 'Премиум'),
)

class ProfileForm(forms.ModelForm):
    region = forms.ChoiceField(choices=BELARUS_REGIONS, label="Область", required=True)
    phone = forms.CharField(label="Телефон", required=True)
    city = forms.CharField(label="Город", required=True)
    full_name = forms.CharField(label="Имя", required=True)
    workshop_name = forms.CharField(label="Название магазина или мастерской (не заполняйте, если магазина, мастерской нет)", required=False)
    delivery_methods = forms.CharField(
        label="Способы отправки",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False
    )
    tariff = forms.ChoiceField(choices=TARIFF_CHOICES, label="Тарифный план", required=True)

    class Meta:
        model = Profile
        fields = ['full_name', 'phone', 'region', 'city', 'workshop_name', 'delivery_methods', 'tariff']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Независимо от текущего тарифа, мы всегда скрываем и блокируем поле tariff,
        # чтобы изменение тарифа происходило только через процесс подписки.
        self.fields['tariff'].widget = forms.HiddenInput()
        self.fields['tariff'].disabled = True

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def __init__(self, *args, **kwargs):
        self.reviewer = kwargs.pop('reviewer', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        # Проверяем, что пользователь не оставляет отзыв самому себе
        if self.reviewer == self.user:
            raise forms.ValidationError("Нельзя оставлять отзыв самому себе.")
        if Review.objects.filter(user=self.user, reviewer=self.reviewer).exists():
            raise forms.ValidationError("Вы уже оставили отзыв этому пользователю.")
        return cleaned_data