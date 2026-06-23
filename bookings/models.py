from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime

def validate_image_size(value):
    """Validate that the image file is not too large"""
    filesize = value.size
    if filesize > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(f"Maximum file size is 5MB. Your file is {filesize / 1048576:.1f}MB.")
    return value

class Resource(models.Model):
    """A bookable resource (e.g., a tutor, a room, equipment)"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('INACTIVE', 'Inactive'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='resources',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='APPROVED'
    )
    location = models.CharField(max_length=200, blank=True, null=True)
    max_capacity = models.PositiveIntegerField(default=1, help_text="Maximum number of people that can book this resource")
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    
    # Image field
    image = models.ImageField(
        upload_to='resources/', 
        blank=True, 
        null=True,
        validators=[validate_image_size],
        help_text="Upload an image of your resource (max 5MB)"
    )
    
    # Keep image_url for backward compatibility
    image_url = models.URLField(blank=True, null=True, help_text="Optional: Link to an image URL")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_image_url(self):
        """Get the image URL (prefer uploaded image over URL)"""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return '/static/bookings/images/default-resource.png'
    
    def has_image(self):
        """Check if the resource has an image"""
        return bool(self.image) or bool(self.image_url)
    
    def can_edit(self, user):
        """Check if a user can edit this resource"""
        return user.is_authenticated and (user == self.owner or user.is_staff)
    
    def can_delete(self, user):
        """Check if a user can delete this resource"""
        return user.is_authenticated and (user == self.owner or user.is_staff)
    
    def is_approved(self):
        """Check if the resource is approved"""
        return self.status == 'APPROVED'
    
    def is_public(self):
        """Check if the resource is visible to everyone"""
        return self.status in ['APPROVED']

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
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
