from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_review_submitted_email(review):
    """Send confirmation when review is submitted"""
    subject = f'Review Submitted for "{review.resource.name}"'
    
    context = {
        'review': review,
        'user': review.user,
        'resource': review.resource,
        'site_url': 'http://127.0.0.1:8000',
    }
    
    html_message = render_to_string('emails/review_submitted.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [review.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_review_approved_email(review):
    """Send email when review is approved"""
    subject = f'Your review for "{review.resource.name}" has been approved!'
    
    context = {
        'review': review,
        'user': review.user,
        'resource': review.resource,
        'site_url': 'http://127.0.0.1:8000',  # Update with your domain
    }
    
    html_message = render_to_string('emails/review_approved.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [review.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_review_rejected_email(review):
    """Send email when review is rejected"""
    subject = f'Your review for "{review.resource.name}" needs revision'
    
    context = {
        'review': review,
        'user': review.user,
        'resource': review.resource,
        'site_url': 'http://127.0.0.1:8000',  # Update with your domain
    }
    
    html_message = render_to_string('emails/review_rejected.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [review.user.email],
        html_message=html_message,
        fail_silently=False,
    )