from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime

class Resource(models.Model):
    """A bookable resource (e.g., a tutor, a room, a equipment)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Booking(models.Model):
    """A booking for a specific resource at a specific time"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure no overlapping bookings for the same resource
        constraints = [
            models.UniqueConstraint(
                fields=['resource', 'start_time', 'end_time'],
                name='unique_booking_slot'
            )
        ]
        indexes = [
            models.Index(fields=['resource', 'start_time']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.resource.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def clean(self):
        """Validate that end_time is after start_time"""
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
