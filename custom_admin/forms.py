from django import forms
from django.utils.safestring import mark_safe



# Форма для редактирования
class DataEditForm(forms.Form):
    # Поле для выбора устройства
    device_name = forms.ChoiceField(choices=[])

    # Поле для выбора бренда (зависит от выбранного устройства)
    brand_name = forms.ChoiceField(choices=[], required=False)

    # Поле для выбора модели (зависит от выбранного бренда)
    model_name = forms.ChoiceField(choices=[], required=False)

    # Поле для выбора типа части
    part_type = forms.ChoiceField(choices=[], required=False)

    # Поле для выбора цвета (зависит от выбранного типа части)
    color = forms.ChoiceField(choices=[], required=False)

    # Поле для выбора состояния
    condition = forms.ChoiceField(choices=[('Оригинал б/у', 'Оригинал б/у'),
                                           ('Оригинал новый', 'Оригинал новый'),
                                           ('Копия б/у', 'Копия б/у'),
                                           ('Копия новый', 'Копия новый')], required=False)

    # Метод для инициализации формы с данными
    def __init__(self, *args, **kwargs):
        # Получаем данные для устройства из JSON-файла
        device_data = kwargs.pop('device_data', None)
        super().__init__(*args, **kwargs)

        if device_data:
            # Заполняем поле выбора устройства
            self.fields['device_name'].choices = [(device, device) for device in device_data.keys()]

            # Если выбрано устройство, заполняем бренды и модели
            if 'device_name' in self.data:
                device_name = self.data.get('device_name')
                self.fields['brand_name'].choices = [(brand, brand) for brand in device_data[device_name]['brands']]

                if 'brand_name' in self.data:
                    brand_name = self.data.get('brand_name')
                    self.fields['model_name'].choices = [(model, model) for model in device_data[device_name]['models'].get(brand_name, [])]

                if 'model_name' in self.data:
                    model_name = self.data.get('model_name')
                    self.fields['part_type'].choices = [(part, part) for part in device_data[device_name]['part_types']]

                    if 'part_type' in self.data:
                        part_type = self.data.get('part_type')
                        self.fields['color'].choices = [(color, color) for color in device_data[device_name]['colors'].get(part_type, [])]
