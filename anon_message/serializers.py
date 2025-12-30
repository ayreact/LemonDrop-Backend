from rest_framework import serializers
from .models import AnonMessage, MessageReply

class MessageReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReply
        fields = ['reply_content', 'created_at']

class AnonMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(write_only=True, required=False)
    has_email = serializers.SerializerMethodField()
    reply = MessageReplySerializer(read_only=True)

    class Meta:
        model = AnonMessage
        fields = ['id', 'message_content', 'created_at', 'sender_email', 'has_email', 'reply']

    def get_has_email(self, obj):
        return bool(obj.sender_email)
