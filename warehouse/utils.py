import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from pillow_heif import register_heif_opener
from PIL import Image, ImageDraw, ImageFont

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

    if img.width > max_resolution or img.height > max_resolution:
        ratio = min(max_resolution / img.width, max_resolution / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, resample=Image.Resampling.LANCZOS)

    if img.mode != "RGB":
        img = img.convert("RGB")

    output_io = BytesIO()
    img.save(output_io, format="JPEG", quality=85)
    new_filename = image.name.split('.')[0] + '.jpg'
    return ContentFile(output_io.getvalue(), name=new_filename)

def add_watermark_to_image(image_file, watermark_text="MobiRazbor.by", opacity=120):
    """
    Накладывает водяной знак с текстом "MobiRazbor.by" на изображение.
    Принимает file-like объект и возвращает новый ContentFile.
    """
    image = Image.open(image_file).convert("RGBA")
    watermark = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)

    # Укажите корректный путь к шрифту
    font_path = os.path.join(settings.BASE_DIR, "static/fonts/OpenSans-Italic-VariableFont_wdth,wght.ttf")
    # Увеличиваем размер шрифта в два раза: 10% от ширины изображения
    font_size = int(image.size[0] * 0.08)
    font = ImageFont.truetype(font_path, font_size)

    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Задаём отступы: 10 пикселей от правого края и немного выше от нижнего края
    vertical_offset = 20  # Этот отступ поднимает текст вверх, увеличьте при необходимости
    position = (image.size[0] - text_width - 10, image.size[1] - text_height - 10 - vertical_offset)

    draw.text(position, watermark_text, fill=(255, 255, 255, opacity), font=font)
    watermarked_image = Image.alpha_composite(image, watermark)
    watermarked_image = watermarked_image.convert("RGB")

    output_io = BytesIO()
    watermarked_image.save(output_io, format="JPEG", quality=90)
    new_filename = image_file.name.split('.')[0] + '_watermarked.jpg'
    return ContentFile(output_io.getvalue(), name=new_filename)
