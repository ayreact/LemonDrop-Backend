from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status
from .models import AnonMessage, MessageReply

class BlindReplyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.message_url = f'/messages/new_message/{self.user.username}/'

    def test_send_message_with_email(self):
        """Test sending a message with a sender email."""
        data = {
            'message_content': 'Hello there!',
            'sender_email': 'sender@example.com'
        }
        response = self.client.post(self.message_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AnonMessage.objects.count(), 1)
        message = AnonMessage.objects.first()
        self.assertEqual(message.sender_email, 'sender@example.com')

    def test_reply_to_message(self):
        """Test replying to a message creates a reply and sends an email."""
        # Create a message with sender email
        message = AnonMessage.objects.create(
            receiver=self.user,
            message_content='Hello',
            sender_email='sender@example.com'
        )
        
        # Login as receiver
        self.client.force_authenticate(user=self.user)
        
        reply_url = f'/messages/reply/{message.id}/'
        data = {'reply_content': 'Thanks for the message!'}
        
        response = self.client.post(reply_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify reply in DB
        self.assertEqual(MessageReply.objects.count(), 1)
        reply = MessageReply.objects.first()
        self.assertEqual(reply.message, message)
        self.assertEqual(reply.reply_content, 'Thanks for the message!')
        
        # Verify email was sent
        # Note: In tests, emails are sent to the dummy outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"Reply from {self.user.username} on LemonDrop")
        self.assertEqual(mail.outbox[0].to, ['sender@example.com'])
        self.assertIn('Thanks for the message!', str(mail.outbox[0].message())) 

    def test_reply_without_email_fails(self):
        """Test replying to a message without sender email fails."""
        message = AnonMessage.objects.create(
            receiver=self.user,
            message_content='No email provided'
        )
        
        self.client.force_authenticate(user=self.user)
        reply_url = f'/messages/reply/{message.id}/'
        data = {'reply_content': 'Cannot reply'}
        
        response = self.client.post(reply_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_messages_structure(self):
        """Test message retrieval includes has_email and reply fields."""
        # Message with email
        msg1 = AnonMessage.objects.create(
            receiver=self.user,
            message_content='With Email',
            sender_email='test@example.com'
        )
        # Message without email
        msg2 = AnonMessage.objects.create(
            receiver=self.user,
            message_content='No Email'
        )
        # Reply to msg1
        MessageReply.objects.create(message=msg1, reply_content="Replying")

        self.client.force_authenticate(user=self.user)
        url = f'/messages/retrieve/{self.user.username}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check msg1 (should have has_email=True, reply!=None)
        # Ordering might be by created_at, default is usually by ID or creation? 
        # API doesn't specify sort order, but typically it is retrieval.
        # Let's find msg1 in response
        res_msg1 = next(m for m in response.data if m['id'] == msg1.id)
        self.assertTrue(res_msg1['has_email'])
        self.assertIsNotNone(res_msg1['reply'])
        self.assertEqual(res_msg1['reply']['reply_content'], "Replying")

        # Check msg2 (should have has_email=False, reply=None)
        res_msg2 = next(m for m in response.data if m['id'] == msg2.id)
        self.assertFalse(res_msg2['has_email'])
        self.assertIsNone(res_msg2['reply'])
