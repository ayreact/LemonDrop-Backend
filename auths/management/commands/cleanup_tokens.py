from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta, datetime, timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from auths.models import BlacklistedAccessToken

class Command(BaseCommand):
    help = 'Deletes expired blacklisted access and refresh tokens.'

    def handle(self, *args, **kwargs):
        # 1. Delete blacklisted access tokens older than 1 day
        expiration_time = now() - timedelta(days=1)
        deleted_access, _ = BlacklistedAccessToken.objects.filter(created_at__lt=expiration_time).delete()
        if deleted_access > 0:
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_access} expired blacklisted access tokens.'))
        
        # 2. Delete expired blacklisted refresh tokens
        # Using simplejwt's logic: deletes tokens where expires_at < now
        current_time = datetime.now(timezone.utc)
        deleted_refresh, _ = BlacklistedToken.objects.filter(token__expires_at__lt=current_time).delete()
        if deleted_refresh > 0:
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_refresh} expired blacklisted refresh tokens.'))
        
        if deleted_access == 0 and deleted_refresh == 0:
            self.stdout.write('No expired tokens found.')
