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
def roadmap_progress_percentage(roadmap, user):
    """Calculate progress percentage for a roadmap."""
    from lms.models import SectionCompletion
    total_sections = 0
    completed_sections = 0
    
    for room in roadmap.rooms.filter(is_active=True):
        room_sections = room.sections.filter(is_active=True)
        total_sections += room_sections.count()
        
        for section in room_sections:
            if SectionCompletion.objects.filter(user=user, section=section, is_completed=True).exists():
                completed_sections += 1
    
    if total_sections == 0:
        return 0
    
    return round((completed_sections / total_sections) * 100)


@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def div(value, arg):
    """Divide the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def sub(value, arg):
    """Subtract the argument from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def abs_filter(value):
    """Return the absolute value."""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0


@register.filter(name='abs')
def abs_builtin(value):
    """Return the absolute value."""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0


@register.filter
def room_progress_percentage(room, user):
    """Calculate progress percentage for a room."""
    from lms.models import SectionCompletion
    
    total_sections = room.sections.filter(is_active=True).count()
    if total_sections == 0:
        return 0
    
    completed_sections = SectionCompletion.objects.filter(
        user=user,
        section__room=room,
        section__is_active=True,
        is_completed=True
    ).count()
    
    return round((completed_sections / total_sections) * 100)


@register.simple_tag
def get_room_progress(user, room):
    """Get room progress as a simple tag."""
    return room_progress_percentage(room, user)


@register.simple_tag
def get_roadmap_progress(user, roadmap):
    """Get roadmap progress as a simple tag."""
    return roadmap_progress_percentage(roadmap, user)


@register.simple_tag
def is_section_completed(user, section):
    """Check if section is completed by user."""
    from lms.models import SectionCompletion
    return SectionCompletion.objects.filter(user=user, section=section, is_completed=True).exists()


@register.simple_tag
def get_user_answer(user, question):
    """Get user's answer for a question."""
    from lms.models import UserAnswer
    try:
        answer = UserAnswer.objects.get(user=user, question=question)
        return answer.answer
    except UserAnswer.DoesNotExist:
        return ""


@register.simple_tag
def get_next_section(current_section):
    """Get the next section in the room."""
    try:
        return current_section.room.sections.filter(
            order__gt=current_section.order,
            is_active=True
        ).order_by('order').first()
    except:
        return None


@register.simple_tag
def is_user_enrolled(user, roadmap):
    """Check if user is enrolled in roadmap."""
    from lms.models import Enrollment
    return Enrollment.objects.filter(user=user, roadmap=roadmap, is_active=True).exists()


@register.simple_tag
def user_section_status(user, section):
    """Get user's status for a section (completed, accessible, locked)."""
    from lms.models import SectionCompletion
    
    # Check if completed
    is_completed = SectionCompletion.objects.filter(user=user, section=section, is_completed=True).exists()
    if is_completed:
        return 'completed'
    
    # Check if accessible (simplified logic)
    if section.order == 1:  # First section is always accessible
        return 'accessible'
    
    # Check if previous section is completed
    prev_section = section.room.sections.filter(
        order__lt=section.order,
        is_active=True
    ).order_by('-order').first()
    
    if prev_section:
        prev_completed = SectionCompletion.objects.filter(user=user, section=prev_section, is_completed=True).exists()
        return 'accessible' if prev_completed else 'locked'
    
    return 'accessible'


@register.simple_tag
def get_room_completion(user, room):
    """Get room completion status for user."""
    from lms.models import RoomCompletion
    try:
        completion = RoomCompletion.objects.get(user=user, room=room)
        return completion
    except RoomCompletion.DoesNotExist:
        return None


@register.filter
def room_completion(room, user):
    """Check if room is completed by user."""
    from lms.models import RoomCompletion
    return RoomCompletion.objects.filter(room=room, user=user, is_completed=True).exists()


@register.filter
def user_achievements(roadmap, user):
    """Get user achievements for a roadmap (placeholder)."""
    # Placeholder for achievements system
    return []


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