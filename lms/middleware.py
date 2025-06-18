"""
Custom middleware for LMS functionality.
"""
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext as _
from django.shortcuts import redirect


class TrialExpirationMiddleware:
    """
    Middleware to handle trial expiration for users.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (request.user.is_authenticated and 
            not request.user.is_paid_user and 
            not request.user.is_trial_active and
            not request.path.startswith('/admin/') and
            not request.path.startswith('/upgrade/') and
            not request.path.startswith('/logout/')):
            
            # Show trial expired message
            messages.warning(
                request, 
                _('Your trial has expired. Please upgrade to continue accessing premium features.')
            )
        
        response = self.get_response(request)
        return response


class CourseProgressMiddleware:
    """
    Middleware to track course progress and analytics.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add global context data that can be used across templates
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Track last activity
            request.user.last_login = timezone.now()
            request.user.save(update_fields=['last_login'])
        
        response = self.get_response(request)
        return response