from django.urls import path
from .views import NewMessageView, RetrieveMessagesView, HealthCheckView, DeleteMessageView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('new_message/<str:username>/', NewMessageView.as_view(), name='submit-message'),
    path('retrieve/<str:username>/', RetrieveMessagesView.as_view(), name='retrieve-messages'),
    path('delete_message/<int:message_id>/', DeleteMessageView.as_view(), name='delete-message'),
]