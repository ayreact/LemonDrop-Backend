from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import AnonMessage

class MessageDeletionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.receiver = User.objects.create_user(username='receiver', password='password')
        self.sender = User.objects.create_user(username='sender', password='password')
        self.message = AnonMessage.objects.create(
            receiver=self.receiver,
            message_content="Secret message",
            is_visible=True
        )
        self.other_message = AnonMessage.objects.create(
            receiver=self.sender,
            message_content="Other message",
            is_visible=True
        )

    def test_delete_message_success(self):
        self.client.force_authenticate(user=self.receiver)
        response = self.client.delete(f'/messages/delete_message/{self.message.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertFalse(self.message.is_visible)

    def test_delete_message_not_owner(self):
        self.client.force_authenticate(user=self.receiver)
        response = self.client.delete(f'/messages/delete_message/{self.other_message.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.other_message.refresh_from_db()
        self.assertTrue(self.other_message.is_visible)

    def test_delete_message_unauthenticated(self):
        response = self.client.delete(f'/messages/delete_message/{self.message.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_visible)

    def test_delete_nonexistent_message(self):
        self.client.force_authenticate(user=self.receiver)
        response = self.client.delete('/messages/delete_message/9999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
