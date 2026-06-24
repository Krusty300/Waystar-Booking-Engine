from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime
from decimal import Decimal
from django.utils import timezone

def validate_image_size(value):
    """Validate that the image file is not too large"""
    filesize = value.size
    if filesize > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(f"Maximum file size is 5MB. Your file is {filesize / 1048576:.1f}MB.")
    return value

class Category(models.Model):
    """Resource category for organizing and filtering resources"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Font Awesome icon class (e.g., 'fa-building')")
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code (e.g., #007bff)")
    
    max_booking_duration = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum booking duration in hours")
    min_booking_duration = models.PositiveIntegerField(blank=True, null=True, help_text="Minimum booking duration in hours")
    requires_approval = models.BooleanField(default=False, help_text="Does this category require admin approval for bookings?")
    booking_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Additional fee for bookings in this category")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Amenity(models.Model):
    """Amenities available for meeting rooms"""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Font Awesome icon class")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class MeetingRoom(models.Model):
    """Extended meeting room features"""
    resource = models.OneToOneField(
        'Resource', 
        on_delete=models.CASCADE, 
        related_name='meeting_room'
    )
    
    # Room identification
    room_number = models.CharField(max_length=20, blank=True, null=True)
    floor_number = models.IntegerField(default=1)
    building_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Capacity tracking
    seating_capacity = models.IntegerField(default=0, help_text="Seating capacity")
    standing_capacity = models.IntegerField(default=0, help_text="Standing capacity")
    classroom_capacity = models.IntegerField(default=0, help_text="Classroom setup capacity")
    theater_capacity = models.IntegerField(default=0, help_text="Theater setup capacity")
    
    # Room features (booleans)
    has_projector = models.BooleanField(default=False)
    has_whiteboard = models.BooleanField(default=False)
    has_video_conferencing = models.BooleanField(default=False)
    has_phone = models.BooleanField(default=False)
    has_smart_tv = models.BooleanField(default=False)
    has_audio_system = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=True)
    has_air_conditioning = models.BooleanField(default=True)
    is_accessible = models.BooleanField(default=True, help_text="Wheelchair accessible")
    
    # Amenities (Many-to-Many)
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='meeting_rooms')
    
    # Room specifications
    room_size_sqft = models.IntegerField(null=True, blank=True, help_text="Room size in square feet")
    natural_light = models.BooleanField(default=False)
    has_window = models.BooleanField(default=True)
    
    # Setup time
    default_setup_time = models.IntegerField(default=15, help_text="Default setup time in minutes")
    default_teardown_time = models.IntegerField(default=15, help_text="Default teardown time in minutes")
    
    # Documents
    floor_plan = models.ImageField(upload_to='floor_plans/', blank=True, null=True)
    room_photo = models.ImageField(upload_to='room_photos/', blank=True, null=True)
    
    # Additional info
    notes = models.TextField(blank=True, help_text="Any additional notes about the room")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.resource.name} (Room {self.room_number or 'N/A'})"
    
    def get_capacity_display(self):
        """Get a formatted string of all capacities"""
        capacities = []
        if self.seating_capacity:
            capacities.append(f"Seating: {self.seating_capacity}")
        if self.standing_capacity:
            capacities.append(f"Standing: {self.standing_capacity}")
        if self.classroom_capacity:
            capacities.append(f"Classroom: {self.classroom_capacity}")
        if self.theater_capacity:
            capacities.append(f"Theater: {self.theater_capacity}")
        return " | ".join(capacities) if capacities else "No capacity data"
    
    def get_amenities_list(self):
        """Get list of amenity names"""
        return [amenity.name for amenity in self.amenities.all()]
    
    def get_features_list(self):
        """Get list of available features"""
        features = []
        if self.has_projector:
            features.append('Projector')
        if self.has_whiteboard:
            features.append('Whiteboard')
        if self.has_video_conferencing:
            features.append('Video Conferencing')
        if self.has_phone:
            features.append('Phone')
        if self.has_smart_tv:
            features.append('Smart TV')
        if self.has_audio_system:
            features.append('Audio System')
        if self.has_wifi:
            features.append('WiFi')
        if self.has_air_conditioning:
            features.append('Air Conditioning')
        return features
    
    def get_max_capacity(self):
        """Get the maximum capacity across all types"""
        return max(
            self.seating_capacity or 0,
            self.standing_capacity or 0,
            self.classroom_capacity or 0,
            self.theater_capacity or 0
        )


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
    
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resources',
        help_text="Select a category for this resource"
    )
    
    # ADD THIS IMAGE FIELD
    image = models.ImageField(
        upload_to='resources/', 
        blank=True, 
        null=True,
        validators=[validate_image_size],
        help_text="Upload an image of your resource (max 5MB)"
    )
    
    # Keep image_url for backward compatibility
    image_url = models.URLField(blank=True, null=True, help_text="Optional: Link to an image URL")
    
    # Meeting room specific images (these can be separate or use the main image)
    room_photo = models.ImageField(
        upload_to='room_photos/', 
        blank=True, 
        null=True,
        help_text="Upload a photo of the room"
    )
    floor_plan = models.ImageField(
        upload_to='floor_plans/', 
        blank=True, 
        null=True,
        help_text="Upload a floor plan of the room"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_image_url(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return '/static/bookings/images/default-resource.png'
    
    def has_image(self):
        return bool(self.image) or bool(self.image_url)
    
    def can_edit(self, user):
        return user.is_authenticated and (user == self.owner or user.is_staff)
    
    def can_delete(self, user):
        return user.is_authenticated and (user == self.owner or user.is_staff)
    
    def is_approved(self):
        return self.status == 'APPROVED'
    
    def is_public(self):
        return self.status in ['APPROVED']
    
    def get_category_rules(self):
        if self.category:
            return {
                'max_duration': self.category.max_booking_duration,
                'min_duration': self.category.min_booking_duration,
                'requires_approval': self.category.requires_approval,
                'booking_fee': self.category.booking_fee,
            }
        return {}
    
    def is_meeting_room(self):
        """Check if this resource has meeting room features"""
        return hasattr(self, 'meeting_room')
    
    def get_meeting_room(self):
        """Get the meeting room instance if it exists"""
        if self.is_meeting_room():
            return self.meeting_room
        return None


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

class UserProfile(models.Model):
    """Extended user profile information"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    bio = models.TextField(max_length=500, blank=True, null=True, help_text="Tell us about yourself")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True,
        help_text="Upload a profile picture"
    )
    
    website = models.URLField(blank=True, null=True, help_text="Your personal website or portfolio")
    twitter = models.CharField(max_length=50, blank=True, null=True, help_text="Twitter username")
    linkedin = models.CharField(max_length=50, blank=True, null=True, help_text="LinkedIn username")
    github = models.CharField(max_length=50, blank=True, null=True, help_text="GitHub username")
    
    email_notifications = models.BooleanField(default=True, help_text="Receive email notifications")
    booking_reminders = models.BooleanField(default=True, help_text="Receive booking reminders")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
    def get_full_name(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        return self.user.username
    
    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/bookings/images/default-avatar.png'
    
    def get_booking_stats(self):
        bookings = Booking.objects.filter(customer=self.user)
        return {
            'total': bookings.count(),
            'upcoming': bookings.filter(
                start_time__gte=timezone.now(),
                status__in=['PENDING', 'CONFIRMED']
            ).count(),
            'completed': bookings.filter(status='COMPLETED').count(),
            'cancelled': bookings.filter(status='CANCELLED').count(),
        }
    
    class Meta:
        verbose_name_plural = "User Profiles"


# ============ ANALYTICS MODELS ============

class AnalyticsEvent(models.Model):
    """Track user events for analytics"""
    EVENT_TYPES = [
        ('VIEW', 'Page View'),
        ('BOOKING', 'Booking Created'),
        ('CANCEL', 'Booking Cancelled'),
        ('SEARCH', 'Search Performed'),
        ('LOGIN', 'User Login'),
        ('SIGNOUT', 'User Signout'),
        ('RESOURCE_CREATE', 'Resource Created'),
        ('RESOURCE_EDIT', 'Resource Edited'),
        ('RESOURCE_DELETE', 'Resource Deleted'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    url = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} by {self.user or 'Anonymous'} at {self.created_at}"

class DailyAnalytics(models.Model):
    """Daily aggregated analytics"""
    date = models.DateField(unique=True)
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    total_bookings = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    page_views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Daily Analytics"
    
    def __str__(self):
        return f"Analytics for {self.date}"


# ============ SIGNALS ============

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
