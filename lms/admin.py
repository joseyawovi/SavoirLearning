"""
Admin interface for Savoir+ LMS.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import (
    User, Roadmap, Room, Section, Question, UserAnswer,
    SectionCompletion, RoomCompletion, Certificate, Payment
)
from .admin_dashboard import admin_dashboard, user_analytics


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    list_display = ('username', 'email', 'is_paid_user', 'trial_end_date', 'is_trial_active')
    list_filter = ('is_paid_user', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('LMS Settings'), {
            'fields': ('is_paid_user', 'trial_start_date', 'trial_end_date')
        }),
    )
    
    readonly_fields = ('trial_start_date',)


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    """Admin interface for Roadmap model."""
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'title_fr', 'description')
    fields = ('title', 'title_fr', 'description', 'description_fr', 'is_active')


class SectionInline(admin.TabularInline):
    """Inline admin for sections within a room."""
    model = Section
    extra = 1
    fields = ('title', 'title_fr', 'order', 'is_active')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin interface for Room model."""
    list_display = ('title', 'roadmap', 'prerequisite_room', 'order', 'is_active')
    list_filter = ('roadmap', 'is_active', 'created_at')
    search_fields = ('title', 'title_fr', 'description')
    fields = ('title', 'title_fr', 'description', 'description_fr', 'roadmap', 'prerequisite_room', 'order', 'is_active')
    inlines = [SectionInline]


class QuestionInline(admin.TabularInline):
    """Inline admin for questions within a section."""
    model = Question
    extra = 1
    fields = ('prompt', 'correct_answer', 'placeholder_hint', 'question_type', 'order', 'is_active')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Admin interface for Section model."""
    list_display = ('title', 'room', 'order', 'is_active')
    list_filter = ('room', 'is_active', 'created_at')
    search_fields = ('title', 'title_fr', 'content')
    fields = ('room', 'title', 'title_fr', 'content', 'content_fr', 'video_url', 'order', 'is_active')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for Question model."""
    list_display = ('prompt', 'section', 'room', 'question_type', 'is_active')
    list_filter = ('question_type', 'is_active', 'created_at')
    search_fields = ('prompt', 'prompt_fr', 'correct_answer')
    fields = ('section', 'room', 'question_type', 'prompt', 'prompt_fr', 'correct_answer', 'placeholder_hint', 'order', 'is_active')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    """Admin interface for UserAnswer model."""
    list_display = ('user', 'question', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'answered_at')
    search_fields = ('user__username', 'question__prompt', 'answer')
    readonly_fields = ('answered_at',)


@admin.register(SectionCompletion)
class SectionCompletionAdmin(admin.ModelAdmin):
    """Admin interface for SectionCompletion model."""
    list_display = ('user', 'section', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'completed_at')
    search_fields = ('user__username', 'section__title')


@admin.register(RoomCompletion)
class RoomCompletionAdmin(admin.ModelAdmin):
    """Admin interface for RoomCompletion model."""
    list_display = ('user', 'room', 'is_completed', 'final_exam_score', 'completed_at')
    list_filter = ('is_completed', 'completed_at')
    search_fields = ('user__username', 'room__title')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin interface for Certificate model."""
    list_display = ('certificate_id', 'user', 'room', 'issued_at', 'is_valid')
    list_filter = ('is_valid', 'issued_at')
    search_fields = ('user__username', 'room__title', 'certificate_id')
    readonly_fields = ('certificate_id', 'issued_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model."""
    list_display = ('transaction_id', 'user', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'currency', 'created_at')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')


class SavoirPlusAdminSite(admin.AdminSite):
    """Custom admin site for Savoir+ LMS."""
    site_header = 'Savoir+ LMS Administration'
    site_title = 'Savoir+ Admin'
    index_title = 'Welcome to Savoir+ LMS Administration'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(admin_dashboard), name='admin_dashboard'),
            path('analytics/', self.admin_view(user_analytics), name='user_analytics'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """Override the default admin index to redirect to custom dashboard."""
        return HttpResponseRedirect(reverse('admin:admin_dashboard'))


# Create custom admin site instance
admin_site = SavoirPlusAdminSite(name='savoir_admin')

# Register all models with the custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(Roadmap, RoadmapAdmin)
admin_site.register(Room, RoomAdmin)
admin_site.register(Section, SectionAdmin)
admin_site.register(Question, QuestionAdmin)
admin_site.register(UserAnswer, UserAnswerAdmin)
admin_site.register(SectionCompletion, SectionCompletionAdmin)
admin_site.register(RoomCompletion, RoomCompletionAdmin)
admin_site.register(Certificate, CertificateAdmin)
admin_site.register(Payment, PaymentAdmin)
