from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class NotificationService:
    
    # ============ EXISTING RESERVATION NOTIFICATIONS ============
    
    @staticmethod
    def send_reservation_confirmed(reservation):
        """Send email when reservation is confirmed"""
        subject = f'Reservation Confirmed: {reservation.equipment.name}'
        message = f"""
        Hello {reservation.user.username},
        
        Your reservation has been CONFIRMED!
        
        Reservation Details:
        Equipment: {reservation.equipment.name}
        Serial Number: {reservation.equipment.serial_number}
        Start Date: {reservation.start_date.strftime('%B %d, %Y at %H:%M')}
        End Date: {reservation.end_date.strftime('%B %d, %Y at %H:%M')}
        Location: {reservation.equipment.location or 'Not specified'}
        
        Your reservation is now confirmed and secured.
        
        View your reservation: /reservations/{reservation.id}/
        
        Thank you for using our equipment rental service!
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [reservation.user.email])
    
    @staticmethod
    def send_reservation_cancelled(reservation):
        """Send email when reservation is cancelled"""
        subject = f'Reservation Cancelled: {reservation.equipment.name}'
        message = f"""
        Hello {reservation.user.username},
        
        Your reservation has been CANCELLED.
        
        Reservation Details:
        Equipment: {reservation.equipment.name}
        Serial Number: {reservation.equipment.serial_number}
        Original Start: {reservation.start_date.strftime('%B %d, %Y at %H:%M')}
        Original End: {reservation.end_date.strftime('%B %d, %Y at %H:%M')}
        
        If you didn't request this cancellation, please contact support.
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [reservation.user.email])
    
    @staticmethod
    def send_reservation_created(reservation):
        """Send email when reservation is created"""
        subject = f'Reservation Created: {reservation.equipment.name}'
        message = f"""
        Hello {reservation.user.username},
        
        Your reservation has been created and is pending approval.
        
        Reservation Details:
        Equipment: {reservation.equipment.name}
        Serial Number: {reservation.equipment.serial_number}
        Start Date: {reservation.start_date.strftime('%B %d, %Y at %H:%M')}
        End Date: {reservation.end_date.strftime('%B %d, %Y at %H:%M')}
        
        Status: PENDING (awaiting staff confirmation)
        This reservation will expire in 24 hours if not confirmed.
        
        View your reservation: /reservations/{reservation.id}/
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [reservation.user.email])
    
    @staticmethod
    def send_reservation_reminder(reservation):
        """Send reminder 24 hours before reservation starts"""
        subject = f'Reminder: {reservation.equipment.name} Reservation Tomorrow'
        message = f"""
        Hello {reservation.user.username},
        
        This is a reminder that your equipment reservation starts tomorrow!
        
        Reservation Details:
        Equipment: {reservation.equipment.name}
        Serial Number: {reservation.equipment.serial_number}
        Start Date: {reservation.start_date.strftime('%B %d, %Y at %H:%M')}
        Location: {reservation.equipment.location or 'Not specified'}
        
        Please arrive on time to collect your equipment.
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [reservation.user.email])
    
    # ============ NEW: RENTAL NOTIFICATIONS ============
    
    @staticmethod
    def send_rental_confirmation(rental):
        """Send confirmation email when equipment is rented"""
        subject = f'Rental Confirmed: {rental.equipment.name}'
        message = f"""
        Hello {rental.rented_by.username},
        
        Your rental has been CONFIRMED!
        
        Rental Details:
        Equipment: {rental.equipment.name}
        Serial Number: {rental.equipment.serial_number}
        Checkout Date: {rental.checkout_date.strftime('%B %d, %Y at %H:%M')}
        Expected Return: {rental.expected_return_date.strftime('%B %d, %Y at %H:%M')}
        Location: {rental.equipment.location or 'Not specified'}
        Condition Notes: {rental.condition_on_checkout or 'None'}
        
        Please return the equipment by the expected return date.
        Late returns may incur penalties.
        
        View your rentals: /my-rentals/
        View equipment: /equipment/{rental.equipment.id}/
        
        Thank you for using our equipment rental service!
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [rental.rented_by.email])
    
    @staticmethod
    def send_return_reminder(rental):
        """Send reminder email when rental is due soon"""
        days_left = (rental.expected_return_date - timezone.now()).days
        
        if days_left > 5:
            return  # Only send for rentals due in 5 days or less
        
        subject = f'Return Reminder: {rental.equipment.name}'
        message = f"""
        Hello {rental.rented_by.username},
        
        This is a reminder that your rental is due for return.
        
        Rental Details:
        Equipment: {rental.equipment.name}
        Serial Number: {rental.equipment.serial_number}
        Checkout Date: {rental.checkout_date.strftime('%B %d, %Y')}
        Expected Return: {rental.expected_return_date.strftime('%B %d, %Y at %H:%M')}
        Days Left: {days_left} days
        
        Please ensure the equipment is returned in good condition.
        
        Return now: /my-rentals/
        
        If you need to extend the rental, please contact support as soon as possible.
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [rental.rented_by.email])
    
    @staticmethod
    def send_overdue_notification(rental):
        """Send notification when rental is overdue"""
        days_overdue = (timezone.now() - rental.expected_return_date).days
        
        subject = f'OVERDUE: {rental.equipment.name}'
        message = f"""
        Hello {rental.rented_by.username},
        
        Your rental is now OVERDUE!
        
        Please return the equipment immediately to avoid additional penalties.
        
        Rental Details:
        Equipment: {rental.equipment.name}
        Serial Number: {rental.equipment.serial_number}
        Expected Return: {rental.expected_return_date.strftime('%B %d, %Y at %H:%M')}
        Days Overdue: {days_overdue} days
        
        Late fees may apply for overdue rentals.
        
        Return now: /my-rentals/
        
        If you have already returned the equipment, please ignore this message.
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [rental.rented_by.email])
    
    # ============ NEW: MAINTENANCE NOTIFICATIONS ============
    
    @staticmethod
    def send_maintenance_scheduled(maintenance):
        """Send notification when maintenance is scheduled"""
        equipment = maintenance.equipment
        owner_email = equipment.owner.email if equipment.owner else None
        
        if not owner_email:
            return
        
        subject = f'Maintenance Scheduled: {equipment.name}'
        message = f"""
        Hello {equipment.owner.username if equipment.owner else 'Equipment Owner'},
        
        Maintenance has been scheduled for your equipment.
        
        Maintenance Details:
        Equipment: {equipment.name}
        Serial Number: {equipment.serial_number}
        Type: {maintenance.get_maintenance_type_display()}
        Title: {maintenance.title}
        Description: {maintenance.description}
        Scheduled Date: {maintenance.scheduled_date.strftime('%B %d, %Y')}
        {'Vendor: ' + maintenance.vendor if maintenance.vendor else ''}
        
        The equipment will be unavailable during the maintenance period.
        
        View maintenance: /equipment-maintenance/
        View equipment: /equipment/{equipment.id}/
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [owner_email])
    
    @staticmethod
    def send_maintenance_completed(maintenance):
        """Send notification when maintenance is completed"""
        equipment = maintenance.equipment
        owner_email = equipment.owner.email if equipment.owner else None
        
        if not owner_email:
            return
        
        subject = f'Maintenance Completed: {equipment.name}'
        message = f"""
        Hello {equipment.owner.username if equipment.owner else 'Equipment Owner'},
        
        The maintenance for your equipment has been COMPLETED.
        
        Maintenance Details:
        Equipment: {equipment.name}
        Serial Number: {equipment.serial_number}
        Type: {maintenance.get_maintenance_type_display()}
        Title: {maintenance.title}
        Completed Date: {maintenance.completed_date.strftime('%B %d, %Y') if maintenance.completed_date else 'N/A'}
        Cost: ${maintenance.cost if maintenance.cost else 'Not specified'}
        
        Your equipment is now available for use.
        
        View equipment: /equipment/{equipment.id}/
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [owner_email])
    
    # ============ NEW: WEEKLY SUMMARY ============
    
    @staticmethod
    def send_weekly_summary(user):
        """Send weekly rental summary to user"""
        from ..models import EquipmentRental, EquipmentReservation
        
        # Get active rentals
        active_rentals = EquipmentRental.objects.filter(
            rented_by=user,
            status='CHECKED_OUT'
        )[:10]
        
        # Get upcoming reservations
        upcoming_reservations = EquipmentReservation.objects.filter(
            user=user,
            start_date__gte=timezone.now(),
            status__in=['PENDING', 'CONFIRMED']
        )[:10]
        
        if not active_rentals and not upcoming_reservations:
            return
        
        subject = 'Your Weekly Rental Summary'
        
        # Build active rentals section
        active_rentals_text = ""
        if active_rentals:
            active_rentals_text = "\nActive Rentals:\n"
            for rental in active_rentals:
                status = "OVERDUE" if rental.is_overdue() else "Active"
                active_rentals_text += f"  • {rental.equipment.name} - Due: {rental.expected_return_date.strftime('%B %d, %Y')} - {status}\n"
        else:
            active_rentals_text = "\nNo active rentals.\n"
        
        # Build upcoming reservations section
        upcoming_text = ""
        if upcoming_reservations:
            upcoming_text = "\nUpcoming Reservations:\n"
            for res in upcoming_reservations:
                upcoming_text += f"  • {res.equipment.name} - Starts: {res.start_date.strftime('%B %d, %Y at %H:%M')}\n"
        else:
            upcoming_text = "\nNo upcoming reservations.\n"
        
        message = f"""
        Hello {user.username},
        
        Here's your weekly rental summary:
        
        {active_rentals_text}
        {upcoming_text}
        
        Quick Actions:
        • View all rentals: /my-rentals/
        • Browse equipment: /equipment/
        • View reservations: /reservations/
        
        Thank you for using our equipment rental service!
        """
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])