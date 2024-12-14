from django import forms
from .models import Part, PartImage
from django.forms import modelformset_factory
from django.core.exceptions import ValidationError
import os

# Разрешённые форматы изображений и максимальный размер файла (в МБ)
ALLOWED_IMAGE_FORMATS = ['.jpeg', '.jpg', '.png', '.heic']
MAX_FILE_SIZE_MB = 5

class PartForm(forms.ModelForm):
    price = forms.IntegerField(min_value=0, label="Цена")
    chip_label = forms.CharField(
        max_length=200,
        required=False,
        label="Маркировка микросхемы",
        widget=forms.TextInput(attrs={'class': 'chip-label', 'style': 'display:none;'})
    )

    class Meta:
        model = Part
        fields = ['device', 'brand', 'model', 'part_type', 'condition', 'color', 'quantity', 'price', 'note', 'chip_label']


class PartImageForm(forms.ModelForm):
    class Meta:
        model = PartImage
        fields = ['image']

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not image:
            return image

        # Проверяем размер файла
        if image.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError(f"Размер файла не должен превышать {MAX_FILE_SIZE_MB} МБ.")

        # Проверяем формат файла
        file_extension = os.path.splitext(image.name)[1].lower()
        if file_extension not in ALLOWED_IMAGE_FORMATS:
            raise ValidationError("Допустимы только форматы JPEG, JPG, PNG и HEIC.")

        return image


# Создание FormSet с использованием PartImageForm и поддержкой до 5 изображений
PartImageFormSet = modelformset_factory(
    PartImage,
    form=PartImageForm,
    extra=5,  # Позволяет добавлять до 5 изображений
    can_delete=True  # Возможность удалять изображения
)
