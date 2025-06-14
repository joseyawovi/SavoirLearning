
"""
Custom admin dashboard views for Savoir+ LMS.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from django import models
from .models import (
    User, Roadmap, Room, Section, Question,
    UserAnswer, SectionCompletion, RoomCompletion,
    Certificate, Payment
)


@staff_member_required
def admin_dashboard(request):
    """Enhanced admin dashboard with analytics."""
    # User statistics
    total_users = User.objects.count()
    trial_users = User.objects.filter(is_paid_user=False).count()
    premium_users = User.objects.filter(is_paid_user=True).count()
    active_trials = User.objects.filter(
        is_paid_user=False,
        trial_end_date__gt=timezone.now()
    ).count()
    
    # Content statistics
    total_roadmaps = Roadmap.objects.filter(is_active=True).count()
    total_rooms = Room.objects.filter(is_active=True).count()
    total_sections = Section.objects.filter(is_active=True).count()
    total_questions = Question.objects.filter(is_active=True).count()
    
    # Progress statistics
    total_certificates = Certificate.objects.filter(is_valid=True).count()
    completed_rooms = RoomCompletion.objects.filter(is_completed=True).count()
    completed_sections = SectionCompletion.objects.filter(is_completed=True).count()
    
    # Payment statistics
    total_revenue = Payment.objects.filter(status='successful').aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    successful_payments = Payment.objects.filter(status='successful').count()
    
    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    new_certificates_week = Certificate.objects.filter(issued_at__gte=week_ago).count()
    new_payments_week = Payment.objects.filter(
        created_at__gte=week_ago,
        status='successful'
    ).count()
    
    # Top performing content
    popular_rooms = Room.objects.annotate(
        completion_count=Count('roomcompletion', filter=Q(roomcompletion__is_completed=True))
    ).order_by('-completion_count')[:5]
    
    # Recent users
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Recent certificates
    recent_certificates = Certificate.objects.select_related(
        'user', 'room'
    ).order_by('-issued_at')[:10]
    
    context = {
        # User stats
        'total_users': total_users,
        'trial_users': trial_users,
        'premium_users': premium_users,
        'active_trials': active_trials,
        
        # Content stats
        'total_roadmaps': total_roadmaps,
        'total_rooms': total_rooms,
        'total_sections': total_sections,
        'total_questions': total_questions,
        
        # Progress stats
        'total_certificates': total_certificates,
        'completed_rooms': completed_rooms,
        'completed_sections': completed_sections,
        
        # Payment stats
        'total_revenue': total_revenue,
        'successful_payments': successful_payments,
        
        # Recent activity
        'new_users_week': new_users_week,
        'new_certificates_week': new_certificates_week,
        'new_payments_week': new_payments_week,
        
        # Data for charts and lists
        'popular_rooms': popular_rooms,
        'recent_users': recent_users,
        'recent_certificates': recent_certificates,
    }
    
    return render(request, 'admin/custom_dashboard.html', context)


@staff_member_required
def user_analytics(request):
    """Detailed user analytics page."""
    # User registration over time (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_registrations = []
    
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        count = User.objects.filter(
            date_joined__date=date.date()
        ).count()
        daily_registrations.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Trial conversion rate
    total_trial_users = User.objects.filter(is_paid_user=False).count()
    converted_users = User.objects.filter(is_paid_user=True).count()
    conversion_rate = (converted_users / (total_trial_users + converted_users) * 100) if (total_trial_users + converted_users) > 0 else 0
    
    # User engagement
    active_users_week = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    context = {
        'daily_registrations': daily_registrations,
        'conversion_rate': round(conversion_rate, 2),
        'active_users_week': active_users_week,
    }
    
    return render(request, 'admin/user_analytics.html', context)
