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

        serializer = AnonMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(receiver=receiver)
            return Response({'message': f'Message sent successfully to {receiver.username}!'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Message Reply
from .serializers import MessageReplySerializer
from .models import MessageReply
from .utils import send_reply_email

class ReplyMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        # Get the original message
        original_message = get_object_or_404(AnonMessage, id=message_id)

        # Check if user is the receiver of the message
        if original_message.receiver != request.user:
            return Response({'error': 'You can only reply to your own messages.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if message has a sender email
        if not original_message.sender_email:
            return Response({'error': 'This message does not have a return address.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already replied
        if hasattr(original_message, 'reply'):
             return Response({'error': 'You have already replied to this message.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MessageReplySerializer(data=request.data)
        if serializer.is_valid():
            reply = serializer.save(message=original_message)
            
            # Send email
            email_sent = send_reply_email(reply)
            
            msg = 'Reply sent successfully!'
            if not email_sent:
                msg += ' (Email delivery failed, but reply saved)'

            return Response({'message': msg}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                is_visible=True,
                created_at__gte=now() - timedelta(hours=36), 
                created_at__lte=now() - timedelta(seconds=0) 
            )

            # Serialize the messages
            serializer = AnonMessageSerializer(messages, many=True)
            return Response(serializer.data)
        except (ValidationError, IndexError, KeyError):
            return Response({"error": "Invalid tokens"}, status=status.HTTP_400_BAD_REQUEST)

# Message Deletion
class DeleteMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, message_id):
        try:
            # Get the message
            message = get_object_or_404(AnonMessage, id=message_id)

            # Check if the requester is the receiver (owner) of the message
            if message.receiver != request.user:
                return Response(
                    {'error': 'You do not have permission to delete this message.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            # Soft delete the message
            message.is_visible = False
            message.save()

            return Response(
                {'message': 'Message deleted successfully.'}, 
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': 'An unexpected error occurred.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
