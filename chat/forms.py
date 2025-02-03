from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'maxlength': '500'})  # Ограничение в HTML
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) > 500:
            raise forms.ValidationError("Сообщение не может превышать 500 символов.")
        return text
