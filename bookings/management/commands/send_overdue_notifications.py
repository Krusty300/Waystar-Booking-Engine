from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import EquipmentRental
from bookings.services.notification_service import NotificationService

class Command(BaseCommand):
    help = 'Send overdue notifications for rentals'

    def handle(self, *args, **options):
        self.stdout.write('Sending overdue notifications...')
        
        # Get overdue rentals
        overdue = EquipmentRental.objects.filter(
            status='CHECKED_OUT',
            expected_return_date__lt=timezone.now()
        )
        
        count = 0
        for rental in overdue:
            try:
                NotificationService.send_overdue_notification(rental)
                count += 1
                self.stdout.write(f'✓ Overdue notification sent for {rental.equipment.name}')
            except Exception as e:
                self.stdout.write(f'✗ Error sending overdue notification for {rental.equipment.name}: {e}')
        
        self.stdout.write(f'Sent {count} overdue notifications')