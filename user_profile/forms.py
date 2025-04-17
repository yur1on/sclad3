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
    ('free', 'Беспла́тный'),
    ('lite', 'Базовый'),
    ('standard', 'Cтандартный'),
    ('standard2', 'Продвинутый'),
    ('standard3', 'Профессиональный'),
    ('premium', 'Неограниченный'),
)

class ProfileForm(forms.ModelForm):
    region = forms.ChoiceField(choices=BELARUS_REGIONS, label="Область", required=True)
    phone = forms.CharField(label="Телефон", required=True)
    city = forms.CharField(label="Город", required=True)
    full_name = forms.CharField(label="Имя", required=True)
    workshop_name = forms.CharField(
        label="Название магазина или мастерской (не заполняйте, если магазина, мастерской нет)",
        required=False
    )
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
        self.fields['tariff'].widget = forms.HiddenInput()
        self.fields['tariff'].disabled = True

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        # Удаляем все пробелы из номера
        phone_clean = phone.replace(" ", "")
        return phone_clean

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(required=False, initial=5)  # Делаем поле необязательным с начальным значением 5

    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def __init__(self, *args, **kwargs):
        self.reviewer = kwargs.pop('reviewer', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.reviewer == self.user:
            raise forms.ValidationError("Нельзя оставлять отзыв самому себе.")
        if Review.objects.filter(user=self.user, reviewer=self.reviewer).exists():
            raise forms.ValidationError("Вы уже оставили отзыв этому пользователю.")
        return cleaned_data
