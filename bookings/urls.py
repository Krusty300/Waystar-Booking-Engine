from django.urls import path
from . import views

urlpatterns = [
    # Calendar View
    path('calendar/', views.CalendarView.as_view(), name='calendar_view'),

    # Resource listing and booking
    path('', views.resource_list, name='resource_list'),
    path('resource/<int:resource_id>/', views.resource_detail, name='resource_detail'),
    
    # User resource management
    path('my-resources/', views.my_resources, name='my_resources'),
    path('resource/create/', views.create_resource, name='create_resource'),
    path('resource/<int:resource_id>/edit/', views.edit_resource, name='edit_resource'),
    path('resource/<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),

    # User profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('booking-history/', views.booking_history, name='booking_history'),
    
    # Admin resource management
    path('manage-resources/', views.admin_manage_resources, name='admin_manage_resources'),
    path('manage-resource/<int:resource_id>/status/', views.admin_update_resource_status,     name='admin_update_resource_status'),
    path('analytics/', views.admin_dashboard, name='admin_dashboard'),
    
    # Booking management
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('my-bookings/export/', views.export_bookings, name='export_bookings'),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    
    # API endpoints
    path('api/available-times/', views.get_available_times, name='get_available_times'),
    path('api/book/', views.book_slot, name='book_slot'),
    
    # Category management (admin only)
    path('categories/', views.manage_categories, name='manage_categories'),
    path('category/create/', views.create_category, name='create_category'),
    path('category/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),


    # Review URLs
    path('resource/<int:resource_id>/write-review/', views.write_review, name='write_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('my-review-history/', views.my_review_history, name='my_review_history'),
    path('resource/<int:resource_id>/reviews/', views.resource_reviews, name='resource_reviews'),
    path('api/review/<int:review_id>/helpful/', views.toggle_review_helpful, name='toggle_review_helpful'),

    # Admin Review URLs - Changed from 'admin/reviews/' to 'reviews-admin/'
    path('reviews-admin/', views.admin_reviews, name='admin_reviews'),
    path('reviews-admin/<int:review_id>/', views.admin_review_detail, name='admin_review_detail'),
    path('reviews-admin/bulk-action/', views.admin_bulk_action_reviews, name='admin_bulk_action_reviews'),
   
]