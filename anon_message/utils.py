from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import threading

class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            subject=self.subject,
            message="",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=self.recipient_list,
            html_message=self.html_content,
            fail_silently=False, 
        )

def send_reply_email(reply_instance):
    """
    Sends an email to the original sender with the reply content.
    """
    try:
        original_message = reply_instance.message
        sender_email = original_message.sender_email
        
        if not sender_email:
            return False

        subject = f"Reply from {original_message.receiver.username} on LemonDrop"
        
        context = {
            'username': original_message.receiver.username,
            'original_message': original_message.message_content,
            'reply_content': reply_instance.reply_content,
        }

        html_content = render_to_string('emails/reply_email.html', context)

        EmailThread(subject, html_content, [sender_email]).start()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
