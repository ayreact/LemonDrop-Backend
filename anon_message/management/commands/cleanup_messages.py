from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta
from anon_message.models import AnonMessage

class Command(BaseCommand):
    help = 'Hides messages older than 36h and deletes messages older than 30 days.'

    def handle(self, *args, **kwargs):
        # 1. Hide messages older than 36 hours
        hide_threshold = now() - timedelta(hours=36)
        updated_count = AnonMessage.objects.filter(timestamp__lt=hide_threshold, is_visible=True).update(is_visible=False)
        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Hidden {updated_count} messages older than 36 hours.'))
        else:
            self.stdout.write('No messages needed hiding.')

        # 2. Delete messages older than 30 days
        delete_threshold = now() - timedelta(days=30)
        deleted_count, _ = AnonMessage.objects.filter(timestamp__lt=delete_threshold).delete()
        if deleted_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} messages older than 30 days.'))
        else:
            self.stdout.write('No messages needed deleting.')
