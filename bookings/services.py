from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from .models import Booking, Resource

class BookingService:
    """Service class to handle booking creation with concurrency control"""
    
    @staticmethod
    @transaction.atomic
    def create_booking(resource_id, customer, start_time, end_time, notes=None):
        """
        Create a booking with database-level locking to prevent double-booking.
        Returns the created Booking object or raises an exception.
        """
        # Validate times
        if start_time >= end_time:
            raise ValidationError("End time must be after start time")
        
        if start_time < timezone.now():
            raise ValidationError("Cannot book in the past")
        
        # Lock the resource to check for conflicts
        resource = Resource.objects.select_for_update().get(id=resource_id)
        
        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            resource=resource,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=['PENDING', 'CONFIRMED']
        ).exists()
        
        if overlapping:
            raise ValidationError("This time slot is already booked")
        
        # Create the booking with notes
        booking = Booking.objects.create(
            resource=resource,
            customer=customer,
            start_time=start_time,
            end_time=end_time,
            status='CONFIRMED',
            notes=notes,
        )
        
        return booking