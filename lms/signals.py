"""
Signals for automatic section completion and progress tracking.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import UserAnswer, SectionCompletion, RoomCompletion


@receiver(post_save, sender=UserAnswer)
def check_section_completion(sender, instance, created, **kwargs):
    """
    Automatically mark section as completed when all questions are answered correctly.
    """
    if not created or not instance.is_correct:
        return
    
    question = instance.question
    if not question.section:
        return
    
    # Get all questions for this section
    section_questions = question.section.questions.filter(is_active=True)
    
    # Get all user answers for this section
    user_answers = UserAnswer.objects.filter(
        user=instance.user,
        question__in=section_questions
    )
    
    # Check if all questions are answered correctly
    if (user_answers.count() == section_questions.count() and
        all(answer.is_correct for answer in user_answers)):
        
        # Mark section as completed
        section_completion, created = SectionCompletion.objects.update_or_create(
            user=instance.user,
            section=question.section,
            defaults={
                'is_completed': True,
                'completed_at': timezone.now(),
            }
        )
        
        # Check if all sections in the room are completed
        room = question.section.room
        room_sections = room.sections.filter(is_active=True)
        completed_sections = SectionCompletion.objects.filter(
            user=instance.user,
            section__in=room_sections,
            is_completed=True
        ).count()
        
        # If all sections completed, ensure room completion record exists
        if completed_sections == room_sections.count():
            RoomCompletion.objects.get_or_create(
                user=instance.user,
                room=room,
                defaults={'is_completed': False}  # Still need final exam
            )


@receiver(post_save, sender=SectionCompletion)
def auto_complete_content_sections(sender, instance, created, **kwargs):
    """
    Auto-complete sections that have no quiz questions (content-only).
    """
    if created and not instance.is_completed:
        # Check if section has no questions
        section_questions = instance.section.questions.filter(is_active=True)
        
        if not section_questions.exists():
            # Auto-complete content-only sections
            instance.is_completed = True
            instance.completed_at = timezone.now()
            instance.save()