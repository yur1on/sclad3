from django import forms
from .models import Profile
from django import forms
from .models import Review

# Полный список областей и городов Беларуси
BELARUS_REGIONS = [
    ('Минская область', 'Минская область'),
    ('Гомельская область', 'Гомельская область'),
    ('Гродненская область', 'Гродненская область'),
    ('Витебская область', 'Витебская область'),
    ('Брестская область', 'Брестская область'),
    ('Могилевская область', 'Могилёвская область'),
]


class ProfileForm(forms.ModelForm):
    region = forms.ChoiceField(choices=BELARUS_REGIONS, label="Область", required=True)
    city = forms.CharField(label="Город", required=True)
    workshop_name = forms.CharField(label="Название мастерской (не заполняйте, если мастерской нет)", required=False)
    delivery_methods = forms.CharField(
        label="Способы отправки",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False
    )  # Новое поле для способов отправки

    class Meta:
        model = Profile
        fields = ['phone', 'region', 'city', 'workshop_name', 'delivery_methods']


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

        # Проверяем, оставил ли этот пользователь уже отзыв
        if Review.objects.filter(user=self.user, reviewer=self.reviewer).exists():
            raise forms.ValidationError("Вы уже оставили отзыв этому пользователю.")

        return cleaned_data
