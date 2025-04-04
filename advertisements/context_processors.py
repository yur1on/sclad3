from .models import Advertisement

def active_advertisements(request):
    # Получаем два последних активных баннера
    ads = Advertisement.objects.filter(active=True).order_by('-created_at')[:2]
    return {'advertisements': ads}
