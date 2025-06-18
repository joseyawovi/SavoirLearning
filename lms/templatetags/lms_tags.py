"""
Custom template tags for LMS.
"""
from django import template
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import timedelta

register = template.Library()


@register.filter
def progress_percentage(current, total):
    """Calculate progress percentage."""
    if total == 0:
        return 0
    return round((current / total) * 100, 1)


@register.filter
def trial_days_remaining(user):
    """Calculate remaining trial days."""
    if user.is_paid_user:
        return None
    
    if user.trial_end_date:
        remaining = (user.trial_end_date - timezone.now()).days
        return max(0, remaining)
    return 0


@register.filter
def format_duration(seconds):
    """Format duration in human readable format."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


@register.inclusion_tag('lms/tags/progress_bar.html')
def progress_bar(current, total, color='primary', show_percentage=True):
    """Render a progress bar component."""
    percentage = progress_percentage(current, total)
    return {
        'current': current,
        'total': total,
        'percentage': percentage,
        'color': color,
        'show_percentage': show_percentage,
    }


@register.inclusion_tag('lms/tags/user_badge.html')
def user_badge(user):
    """Render user status badge."""
    if user.is_paid_user:
        badge_class = 'bg-success'
        badge_text = _('Premium')
        icon = 'fas fa-crown'
    elif user.is_trial_active:
        badge_class = 'bg-warning text-dark-bg'
        badge_text = _('Trial')
        icon = 'fas fa-clock'
    else:
        badge_class = 'bg-danger'
        badge_text = _('Expired')
        icon = 'fas fa-times'
    
    return {
        'user': user,
        'badge_class': badge_class,
        'badge_text': badge_text,
        'icon': icon,
    }


@register.inclusion_tag('lms/tags/section_status.html')
def section_status(section, user):
    """Render section completion status."""
    from lms.models import SectionCompletion
    
    try:
        completion = SectionCompletion.objects.get(user=user, section=section)
        is_completed = completion.is_completed
    except SectionCompletion.DoesNotExist:
        is_completed = False
    
    is_accessible = section.is_accessible_by_user(user)
    
    if is_completed:
        status_class = 'bg-success'
        status_text = _('Completed')
        icon = 'fas fa-check'
    elif is_accessible:
        status_class = 'bg-primary'
        status_text = _('Available')
        icon = 'fas fa-play'
    else:
        status_class = 'bg-gray-600'
        status_text = _('Locked')
        icon = 'fas fa-lock'
    
    return {
        'section': section,
        'is_completed': is_completed,
        'is_accessible': is_accessible,
        'status_class': status_class,
        'status_text': status_text,
        'icon': icon,
    }


@register.simple_tag
def get_completion_rate(user, room):
    """Get completion rate for user in a room."""
    from lms.models import SectionCompletion
    
    sections = room.sections.filter(is_active=True)
    if not sections.exists():
        return 0
    
    completed = SectionCompletion.objects.filter(
        user=user,
        section__in=sections,
        is_completed=True
    ).count()
    
    return progress_percentage(completed, sections.count())


@register.simple_tag
def get_quiz_score(user, section):
    """Get user's quiz score for a section."""
    from lms.models import UserAnswer
    
    questions = section.questions.filter(is_active=True)
    if not questions.exists():
        return None
    
    answers = UserAnswer.objects.filter(
        user=user,
        question__in=questions
    )
    
    if not answers.exists():
        return None
    
    correct_answers = answers.filter(is_correct=True).count()
    return progress_percentage(correct_answers, questions.count())