from django.contrib import admin
from .models import Advertisement

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('partner_name', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('partner_name',)
