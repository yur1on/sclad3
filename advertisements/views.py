from django.shortcuts import render
from .models import Advertisement

def advertisement_view(request):
    ad = Advertisement.objects.filter(active=True).order_by('-created_at').first()  # Берём последний активный баннер
    return render(request, 'advertisements/ad_block.html', {'advertisement': ad})
