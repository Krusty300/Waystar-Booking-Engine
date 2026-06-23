from django.contrib import admin
from .models import Resource, Booking

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