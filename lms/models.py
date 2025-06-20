"""
Models for the Savoir+ LMS application.
"""
import uuid
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Extended user model with trial and payment tracking."""
    is_paid_user = models.BooleanField(default=False, verbose_name=_('Is Paid User'))
    trial_start_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Trial Start Date'))
    trial_end_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Trial End Date'))
    
    def save(self, *args, **kwargs):
        # Set trial_start_date if not set (for superusers and manual creation)
        if not self.trial_start_date:
            from django.utils import timezone
            self.trial_start_date = timezone.now()
        
        # Set trial_end_date if not set
        if not self.trial_end_date and self.trial_start_date:
            self.trial_end_date = self.trial_start_date + timedelta(days=15)
        super().save(*args, **kwargs)
    
    @property
    def is_trial_active(self):
        """Check if user's trial period is still active."""
        if self.is_paid_user:
            return False
        return timezone.now() < self.trial_end_date
    
    @property
    def can_access_quizzes(self):
        """Check if user can access quizzes and exams."""
        return self.is_paid_user
    
    def __str__(self):
        return self.username


class Roadmap(models.Model):
    """Learning roadmap containing multiple rooms."""
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    title_fr = models.CharField(max_length=200, blank=True, verbose_name=_('Title (French)'))
    description = models.TextField(verbose_name=_('Description'))
    description_fr = models.TextField(blank=True, verbose_name=_('Description (French)'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Roadmap')
        verbose_name_plural = _('Roadmaps')
    
    def __str__(self):
        return self.title


class Room(models.Model):
    """Course/Room containing multiple sections."""
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    title_fr = models.CharField(max_length=200, blank=True, verbose_name=_('Title (French)'))
    description = models.TextField(verbose_name=_('Description'))
    description_fr = models.TextField(blank=True, verbose_name=_('Description (French)'))
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='rooms', verbose_name=_('Roadmap'))
    prerequisite_room = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Prerequisite Room'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')
        ordering = ['roadmap', 'order']
    
    def __str__(self):
        return self.title
    
    def is_accessible_by_user(self, user):
        """Check if user can access this room based on prerequisites."""
        from lms.models import Enrollment
        
        # Check if user is enrolled in the roadmap
        is_enrolled = Enrollment.objects.filter(
            user=user,
            roadmap=self.roadmap,
            is_active=True
        ).exists()
        
        print(f"DEBUG: User {user.username} enrolled in roadmap {self.roadmap.title}: {is_enrolled}")
        
        if not is_enrolled:
            print(f"DEBUG: User not enrolled in roadmap, room not accessible")
            return False
        
        # If no prerequisite room, it's accessible
        if not self.prerequisite_room:
            print(f"DEBUG: No prerequisite room, returning True")
            return True
        
        # Check if user has completed the prerequisite room
        prerequisite_completed = RoomCompletion.objects.filter(
            user=user,
            room=self.prerequisite_room,
            is_completed=True
        ).exists()
        
        print(f"DEBUG: Prerequisite room {self.prerequisite_room.title} completed: {prerequisite_completed}")
        return prerequisite_completed


class Section(models.Model):
    """Section within a room containing content and quiz."""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='sections', verbose_name=_('Room'))
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    title_fr = models.CharField(max_length=200, blank=True, verbose_name=_('Title (French)'))
    content = models.TextField(verbose_name=_('Content'))
    content_fr = models.TextField(blank=True, verbose_name=_('Content (French)'))
    video_url = models.URLField(blank=True, verbose_name=_('Video URL'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')
        ordering = ['room', 'order']
    
    def __str__(self):
        return f"{self.room.title} - {self.title}"
    
    def is_accessible_by_user(self, user):
        """Check if user can access this section."""
        # First check if user can access the room
        if not self.room.is_accessible_by_user(user):
            print(f"DEBUG: User {user.username} cannot access room {self.room.title}")
            return False
        
        # Get all sections in this room ordered by order field
        room_sections = Section.objects.filter(
            room=self.room,
            is_active=True
        ).order_by('order')
        
        print(f"DEBUG: Room {self.room.title} has {room_sections.count()} sections")
        print(f"DEBUG: Current section: {self.title} (order: {self.order}, id: {self.id})")
        
        # If no sections exist, this shouldn't happen but just in case
        if not room_sections.exists():
            print("DEBUG: No sections found, returning True")
            return True
        
        # Get the first section (lowest order number)
        first_section = room_sections.first()
        print(f"DEBUG: First section: {first_section.title} (order: {first_section.order}, id: {first_section.id})")
        
        # If this is the first section in the room, it's ALWAYS accessible if room is accessible
        if self.order == first_section.order or self.id == first_section.id:
            print(f"DEBUG: This is the first section, returning True")
            return True
        
        # For other sections, check if the IMMEDIATE previous section is completed
        previous_section = room_sections.filter(order__lt=self.order).order_by('-order').first()
        
        if not previous_section:
            # If no previous sections, this is effectively the first section
            print("DEBUG: No previous sections, returning True")
            return True
        
        # Check if immediate previous section is completed
        previous_completed = SectionCompletion.objects.filter(
            user=user,
            section=previous_section,
            is_completed=True
        ).exists()
        
        print(f"DEBUG: Previous section {previous_section.title} completed: {previous_completed}")
        print(f"DEBUG: Final result: {previous_completed}")
        return previous_completed


class Question(models.Model):
    """Quiz question for a section or final exam."""
    QUESTION_TYPE_CHOICES = [
        ('section', _('Section Quiz')),
        ('final', _('Final Exam')),
    ]
    
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='questions', blank=True, null=True, verbose_name=_('Section'))
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='final_questions', blank=True, null=True, verbose_name=_('Room (for final exam)'))
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, verbose_name=_('Question Type'))
    prompt = models.TextField(verbose_name=_('Question Prompt'))
    prompt_fr = models.TextField(blank=True, verbose_name=_('Question Prompt (French)'))
    correct_answer = models.CharField(max_length=500, verbose_name=_('Correct Answer'))
    placeholder_hint = models.CharField(max_length=100, blank=True, help_text=_('Show placeholder like "_____ _____" to indicate answer format'), verbose_name=_('Placeholder Hint'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ['section', 'room', 'order']
    
    def __str__(self):
        return self.prompt[:50]
    
    def check_answer(self, user_answer):
        """Check if user answer is correct (case-insensitive)."""
        return user_answer.strip().lower() == self.correct_answer.strip().lower()


class UserAnswer(models.Model):
    """User's answer to a question."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_('Question'))
    answer = models.CharField(max_length=500, verbose_name=_('Answer'))
    is_correct = models.BooleanField(verbose_name=_('Is Correct'))
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Answered At'))
    
    class Meta:
        verbose_name = _('User Answer')
        verbose_name_plural = _('User Answers')
        unique_together = ['user', 'question']
    
    def __str__(self):
        return f"{self.user.username} - {self.question.prompt[:30]}"


class SectionCompletion(models.Model):
    """Track user completion of sections."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name=_('Section'))
    is_completed = models.BooleanField(default=False, verbose_name=_('Is Completed'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    
    class Meta:
        verbose_name = _('Section Completion')
        verbose_name_plural = _('Section Completions')
        unique_together = ['user', 'section']
    
    def __str__(self):
        return f"{self.user.username} - {self.section.title}"


class RoomCompletion(models.Model):
    """Track user completion of rooms."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name=_('Room'))
    is_completed = models.BooleanField(default=False, verbose_name=_('Is Completed'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    final_exam_score = models.FloatField(blank=True, null=True, verbose_name=_('Final Exam Score'))
    certificate = models.ForeignKey('Certificate', on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Certificate'))
    
    class Meta:
        verbose_name = _('Room Completion')
        verbose_name_plural = _('Room Completions')
        unique_together = ['user', 'room']
    
    def __str__(self):
        return f"{self.user.username} - {self.room.title}"


class Certificate(models.Model):
    """Certificate issued to users upon room completion."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name=_('Room'))
    certificate_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name=_('Certificate ID'))
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Issued At'))
    is_valid = models.BooleanField(default=True, verbose_name=_('Is Valid'))
    
    class Meta:
        verbose_name = _('Certificate')
        verbose_name_plural = _('Certificates')
        unique_together = ['user', 'room']
    
    def __str__(self):
        return f"Certificate {self.certificate_id} - {self.user.username} - {self.room.title}"


class Enrollment(models.Model):
    """Track user enrollments in specific roadmaps."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, verbose_name=_('Roadmap'))
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Enrolled At'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    
    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        unique_together = ['user', 'roadmap']
    
    def __str__(self):
        return f"{self.user.username} - {self.roadmap.title}"


class Payment(models.Model):
    """Payment transaction records."""
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('successful', _('Successful')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    currency = models.CharField(max_length=3, default='XOF', verbose_name=_('Currency'))
    payment_method = models.CharField(max_length=50, verbose_name=_('Payment Method'))
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name=_('Transaction ID'))
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.user.username} - {self.amount} {self.currency}"
