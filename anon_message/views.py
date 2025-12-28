from django.shortcuts import get_object_or_404
from .models import AnonMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from .serializers import AnonMessageSerializer
from auths.token_check import CheckAccessToken
from rest_framework.permissions import IsAuthenticated, AllowAny

# Health Check View
class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "message": "Service is healthy"}, status=status.HTTP_200_OK)

# Message Submission
class NewMessageView(APIView):
    def post(self, request, username):
        receiver = get_object_or_404(User, username=username)

        message_content = request.data.get('message')

        if not message_content:
            return Response({'error': 'Please type a message!'}, status=status.HTTP_400_BAD_REQUEST)

        new_message = AnonMessage.objects.create(
            message_content=message_content,
            receiver=receiver
        )
        new_message.save()
        return Response({'message': f'Message sent successfully to {receiver.username}!'}, status=status.HTTP_201_CREATED)
    
# Message Retrieval
class RetrieveMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        try:
            access_token = request.headers.get("Authorization", "").split(" ")[1]
            receiver = get_object_or_404(User, username=username)

            valid_token = CheckAccessToken(access_token)
            if valid_token == True:
                return Response({"error": "User already logged out!"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve messages within the allowed timeframe
            messages = AnonMessage.objects.filter(
                receiver=receiver,
                created_at__gte=now() - timedelta(hours=36), 
                created_at__lte=now() - timedelta(seconds=0) 
            )

            # Serialize the messages
            serializer = AnonMessageSerializer(messages, many=True)
            return Response(serializer.data)
        except (ValidationError, IndexError, KeyError):
            return Response({"error": "Invalid tokens"}, status=status.HTTP_400_BAD_REQUEST)
