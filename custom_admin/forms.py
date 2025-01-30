from django import forms
import json

class JSONDataForm(forms.Form):
    json_data = forms.CharField(widget=forms.Textarea, required=True)

    def clean_json_data(self):
        data = self.cleaned_data["json_data"]
        try:
            json.loads(data)  # Проверка, корректный ли JSON
        except json.JSONDecodeError:
            raise forms.ValidationError("Некорректный JSON")
        return data
