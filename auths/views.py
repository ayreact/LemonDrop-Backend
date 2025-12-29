from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.core.exceptions import ValidationError
from .serializers import RegisterSerializer
from .models import BlacklistedAccessToken
from .token_check import CheckAccessToken
from rest_framework_simplejwt.views import TokenRefreshView
from datetime import timedelta

# JWT Token Generation
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # Save user
            tokens = get_tokens_for_user(user)  # Generate tokens
            
            response = Response(
                {
                    "username": user.username,
                    "email": user.email,
                    "access": tokens["access"],  # Send access token in response
                }, 
                status=status.HTTP_201_CREATED
            )

            # Set refresh token as HTTP-only cookie
            response.set_cookie(
                key="refresh_token",
                value=tokens["refresh"],
                httponly=True,  # Prevent access from JavaScript
                secure=settings.USE_HTTPS,  # Secure cookie if using HTTPS
                samesite="Lax",  # Adjust as needed for cross-site requests
                max_age=int(timedelta(days=7).total_seconds()),  # Set expiry (7 days)
            )

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login
class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to log in

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user:
            # Generate JWT tokens
            tokens = get_tokens_for_user(user)

            response = Response({
                "message": "Login successful",
                "access": tokens["access"]  # Return only the access token
            }, status=status.HTTP_200_OK)

            # Set refresh token as HTTP-only cookie
            response.set_cookie(
                key="refresh_token",
                value=tokens["refresh"],
                httponly=True,
                secure=settings.USE_HTTPS,  # Secure cookie if using HTTPS
                samesite="None",  # Adjust based on frontend/backend setup
                max_age=int(timedelta(days=7).total_seconds())  # Expiry in 7 days
            )

            return response
        
        # Return error if authentication fails
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# User Logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get refresh token from HTTP-only cookie
            refresh_token = request.COOKIES.get("refresh_token")
            access_token = request.headers.get("Authorization", "").split(" ")[1]  # Extract access token

            if not refresh_token or not access_token:
                return Response({"error": "Tokens are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist refresh token
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except ValidationError:
                return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)

            # Clear refresh token cookie
            response = Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
            response.delete_cookie("refresh_token")

            return response

        except IndexError:
            return Response({"error": "Invalid access token"}, status=status.HTTP_400_BAD_REQUEST)

# Refrsh token system
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")  

        if not refresh_token:
            return Response({"error": "No refresh token found. Please log in again."}, status=status.HTTP_401_UNAUTHORIZED)

        request.data["refresh"] = refresh_token  

        return super().post(request, *args, **kwargs)  
