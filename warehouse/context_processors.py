# warehouse/context_processors.py

# warehouse/context_processors.py

from .models import Part
from django.contrib.auth.models import User

def counts(request):
    return {
        'part_count': Part.objects.count(),
        'user_count': User.objects.count(),
    }

