from django import forms
from .models import Profile
from django import forms
from .models import Review

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'city']




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
