"""lemonDrop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import cron_job_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('uauth/', include('auths.urls')),
    path('social-auth/', include('socialauths.urls')),
    path('messages/', include('anon_message.urls')),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    # path("auth/social/", include("allauth.socialaccount.urls")),
    path('cron/', cron_job_view, name='cron_trigger'),
]