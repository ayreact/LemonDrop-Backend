from django.contrib import admin
from .models import AnonMessage

@admin.register(AnonMessage)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "receiver", "created_at", "is_visible")  
    search_fields = ("id", "receiver", "created_at", "is_visible")  
    list_filter = ("id", "receiver", "created_at", "is_visible")  
