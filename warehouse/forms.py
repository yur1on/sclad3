from pillow_heif import register_heif_opener

register_heif_opener()
from django import forms
from .models import Part, PartImage
from django.forms import modelformset_factory
from django.core.exceptions import ValidationError
import os
from django import forms
from .models import Part, PartImage
from pillow_heif import register_heif_opener
# Разрешённые форматы изображений и максимальный размер файла (в МБ)
ALLOWED_IMAGE_FORMATS = ['.jpeg', '.jpg', '.png', '.webp', '.heic']
MAX_FILE_SIZE_MB = 5


# warehouse/forms.py


register_heif_opener()

class PartForm(forms.ModelForm):
    price = forms.IntegerField(min_value=0, label="Цена")
    chip_label = forms.CharField(
        max_length=200,
        required=False,
        label="Маркировка микросхемы",
        widget=forms.TextInput(attrs={'class': 'chip-label', 'style': 'display:none;'})
    )
    # Добавляем поле для номера запчасти
    part_number = forms.CharField(
        max_length=100,
        required=False,
        label="Номер запчасти (штрих-код)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Сканируйте или сгенерируется автоматически',
            'autofocus': 'autofocus'
        })
    )

    class Meta:
        model = Part
        fields = ['part_number', 'device', 'brand', 'model', 'part_type', 'condition', 'color', 'quantity', 'price', 'note', 'chip_label']


class PartImageForm(forms.ModelForm):
    class Meta:
        model = PartImage
        fields = ['image']
        # Help text не задаётся здесь, так как он будет выведен один раз в шаблоне

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        # Проверка длины имени файла
        if len(image.name) > 200:
            raise ValidationError("Имя файла не должно превышать 200 символов. Сейчас: {} символов.".format(len(image.name)))

        # Проверка размера файла
        if image.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError(f"Размер файла не должен превышать {MAX_FILE_SIZE_MB} МБ.")

        # Проверка формата файла
        file_extension = os.path.splitext(image.name)[1].lower()
        if file_extension not in ALLOWED_IMAGE_FORMATS:
            raise ValidationError("Допустимы только форматы: JPEG, JPG, PNG, WEBP, HEIC.")

        return image


# Создание FormSet для загрузки до 5 изображений
PartImageFormSet = modelformset_factory(
    PartImage,
    form=PartImageForm,
    extra=5,
    can_delete=True
)
