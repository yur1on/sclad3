
from pillow_heif import register_heif_opener
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
register_heif_opener()
def compress_image(image):
    """
    Обработка изображения:
      - Изменение размера до максимума 1920 пикселей по большей стороне.
      - Конвертация в формат JPEG с качеством 85.
      - Удаление метаданных (EXIF, GPS и т.д.).
    """
    img = Image.open(image)
    max_resolution = 1920

    # Если размеры превышают максимум, масштабируем изображение
    if img.width > max_resolution or img.height > max_resolution:
        ratio = min(max_resolution / img.width, max_resolution / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        # Используем новый метод сглаживания
        img = img.resize(new_size, resample=Image.Resampling.LANCZOS)

    # Если изображение не в режиме RGB, приводим его к RGB
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Сохраняем изображение в формате JPEG без метаданных
    output_io = BytesIO()
    img.save(output_io, format="JPEG", quality=85)
    new_filename = image.name.split('.')[0] + '.jpg'
    return ContentFile(output_io.getvalue(), name=new_filename)
