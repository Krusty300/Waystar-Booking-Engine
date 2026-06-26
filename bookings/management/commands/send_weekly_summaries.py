from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bookings.services.notification_service import NotificationService

class Command(BaseCommand):
    help = 'Send weekly rental summaries to all users'

    def handle(self, *args, **options):
        self.stdout.write('Sending weekly summaries...')
        
        # Get all active users (users who have logged in recently)
        from django.utils import timezone
        from datetime import timedelta
        
        active_users = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=30)
        )
        
        count = 0
        for user in active_users:
            try:
                NotificationService.send_weekly_summary(user)
                count += 1
                self.stdout.write(f'✓ Summary sent to {user.username}')
            except Exception as e:
                self.stdout.write(f'✗ Error sending summary to {user.username}: {e}')
        
        self.stdout.write(f'Sent {count} weekly summaries')