from django.contrib import admin
from .models import BlacklistedAccessToken

@admin.register(BlacklistedAccessToken)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "token", "blacklisted_at")  
    search_fields = ("id", "token", "blacklisted_at")  
    list_filter = ("id", "token", "blacklisted_at")  

