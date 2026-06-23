from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_list, name='resource_list'),
    path('resource/<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('signup/', views.signup, name='signup'),
    
    # API endpoints
    path('api/available-times/', views.get_available_times, name='get_available_times'),
    path('api/book/', views.book_slot, name='book_slot'),
]