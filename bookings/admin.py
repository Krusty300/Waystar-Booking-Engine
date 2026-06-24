from django.contrib import admin
from .models import Resource, Booking
from .models import MeetingRoom, Amenity

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['resource', 'customer', 'start_time', 'end_time', 'status', 'notes_preview']
    list_filter = ['status', 'resource', 'start_time']
    search_fields = ['customer__username', 'resource__name', 'notes']
    ordering = ['-start_time']
    
    def notes_preview(self, obj):
        """Show a preview of the notes in admin"""
        if obj.notes:
            return obj.notes[:50] + ('...' if len(obj.notes) > 50 else '')
        return '-'
    notes_preview.short_description = 'Notes Preview'

@admin.register(MeetingRoom)
class MeetingRoomAdmin(admin.ModelAdmin):
    list_display = ['resource', 'room_number', 'floor_number', 'seating_capacity', 'has_projector', 'has_video_conferencing']
    list_filter = ['floor_number', 'has_projector', 'has_video_conferencing', 'has_wifi']
    search_fields = ['resource__name', 'room_number', 'building_name']
    filter_horizontal = ['amenities']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active']
    search_fields = ['name']