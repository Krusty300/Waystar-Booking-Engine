from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from bookings.models import EquipmentRental
from bookings.services.notification_service import NotificationService

class Command(BaseCommand):
    help = 'Send return reminders for rentals due soon'

    def handle(self, *args, **options):
        self.stdout.write('Sending return reminders...')
        
        # Get rentals due in 1, 2, and 3 days
        due_soon = EquipmentRental.objects.filter(
            status='CHECKED_OUT',
            expected_return_date__gte=timezone.now(),
            expected_return_date__lte=timezone.now() + timedelta(days=3)
        )
        
        count = 0
        for rental in due_soon:
            try:
                NotificationService.send_return_reminder(rental)
                count += 1
                self.stdout.write(f'✓ Reminder sent for {rental.equipment.name}')
            except Exception as e:
                self.stdout.write(f'✗ Error sending reminder for {rental.equipment.name}: {e}')
        
        self.stdout.write(f'Sent {count} return reminders')