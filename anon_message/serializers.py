from rest_framework import serializers
from .models import AnonMessage

class AnonMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnonMessage
        fields = ['id', 'message_content', 'created_at']
