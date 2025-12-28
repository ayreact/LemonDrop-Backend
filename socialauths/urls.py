from django.urls import path
from .views import google_callback, GoogleLogin, get_user_info

urlpatterns = [
    path("google/", GoogleLogin.as_view(), name="google-login"),
    path("google/callback/", google_callback, name="google_callback"),
    path("user-info/", get_user_info, name="user-info"),
]
