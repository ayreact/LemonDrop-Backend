import requests
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.http import JsonResponse
from rest_framework.response import Response

User = get_user_model()
SITE_BASE_URL = settings.SITE_BASE_URL
    
# Google Auth System
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_CALLBACK_URL
    client_class = OAuth2Client

    def get(self, request, *args, **kwargs):
        provider = self.adapter_class.provider_id
        client_id = settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID
        redirect_uri = self.callback_url
        scope = "openid email profile"

        authorization_url = (
            f"https://accounts.google.com/o/oauth2/auth"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope}"
            f"&response_type=code"
            f"&access_type=offline"
        )
        return JsonResponse({"authorization_url": authorization_url})

def google_callback(request):
    code = request.GET.get("code")
    if not code:
        return redirect(f"{settings.LOGIN_REDIRECT_URL}/auth/callback?error=missing_code")

    # Step 1: Exchange code for access token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID,
        "client_secret": settings.SOCIAL_AUTH_GOOGLE_SECRET,
        "redirect_uri": f"{settings.SITE_BASE_URL}/social-auth/google/callback/",
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data)
    token_info = response.json()

    if "error" in token_info:
        return redirect(f"{settings.LOGIN_REDIRECT_URL}/auth/callback?error={token_info['error']}")

    access_token = token_info.get("access_token")

    # Step 2: Fetch user details from Google
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_data = user_info_response.json()

    if "error" in user_data:
        return redirect(f"{settings.LOGIN_REDIRECT_URL}/auth/callback?error={user_data['error']}")

    email = user_data.get("email")
    name = user_data.get("name")

    user, created = User.objects.get_or_create(email=email, defaults={"username": name})

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    response = redirect(f"{settings.LOGIN_REDIRECT_URL}/auth/callback?token={access_token}")
    response.set_cookie(
        "refresh_token",
        str(refresh),
        httponly=True,
        secure=settings.USE_HTTPS,  # Set to False for local testing, True for production with HTTPS
        samesite="None",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )
	
    return response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    return Response({
        "username": user.username,
        "email": user.email
    })
