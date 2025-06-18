"""
Admin interface for Savoir+ LMS.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Q, Sum
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from .models import (
    User, Roadmap, Room, Section, Question, UserAnswer,
    SectionCompletion, RoomCompletion, Certificate, Payment, Enrollment
)


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


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin interface for Enrollment model."""
    list_display = ('user', 'roadmap', 'enrolled_at', 'is_active')
    list_filter = ('is_active', 'enrolled_at', 'roadmap')
    search_fields = ('user__username', 'roadmap__title')
    readonly_fields = ('enrolled_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model."""
    list_display = ('transaction_id', 'user', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'currency', 'created_at')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')


class CustomAdminSite(admin.AdminSite):
    """Custom admin site with dashboard."""
    site_header = "Savoir+ LMS Administration"
    site_title = "Savoir+ Admin"
    index_title = "Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='admin_dashboard'),
            path('analytics/', self.admin_view(self.analytics_view), name='admin_analytics'),
            path('user-management/', self.admin_view(self.user_management_view), name='admin_user_management'),
            path('course-management/', self.admin_view(self.course_management_view), name='admin_course_management'),
            path('export-data/', self.admin_view(self.export_data_view), name='admin_export_data'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """Custom dashboard view with statistics."""
        context = {
            'title': 'Dashboard Overview',
            'total_users': User.objects.count(),
            'paid_users': User.objects.filter(is_paid_user=True).count(),
            'trial_users': User.objects.filter(is_paid_user=False).count(),
            'total_roadmaps': Roadmap.objects.filter(is_active=True).count(),
            'total_rooms': Room.objects.filter(is_active=True).count(),
            'total_sections': Section.objects.filter(is_active=True).count(),
            'completed_rooms': RoomCompletion.objects.filter(is_completed=True).count(),
            'certificates_issued': Certificate.objects.filter(is_valid=True).count(),
            'recent_users': User.objects.order_by('-date_joined')[:10],
            'recent_completions': RoomCompletion.objects.filter(is_completed=True).order_by('-completed_at')[:10],
        }
        return render(request, 'admin/dashboard.html', context)

    def analytics_view(self, request):
        """Analytics view with detailed statistics."""
        # User analytics
        user_stats = {
            'total_users': User.objects.count(),
            'paid_users': User.objects.filter(is_paid_user=True).count(),
            'trial_users': User.objects.filter(is_paid_user=False).count(),
            'active_trials': User.objects.filter(
                is_paid_user=False,
                trial_end_date__gt=timezone.now()
            ).count(),
        }

        # Course analytics
        course_stats = []
        for roadmap in Roadmap.objects.filter(is_active=True):
            rooms = roadmap.rooms.filter(is_active=True)
            total_enrollments = 0
            total_completions = 0
            
            for room in rooms:
                enrollments = RoomCompletion.objects.filter(room=room).count()
                completions = RoomCompletion.objects.filter(room=room, is_completed=True).count()
                total_enrollments += enrollments
                total_completions += completions
            
            completion_rate = (total_completions / total_enrollments * 100) if total_enrollments > 0 else 0
            
            course_stats.append({
                'roadmap': roadmap,
                'total_rooms': rooms.count(),
                'enrollments': total_enrollments,
                'completions': total_completions,
                'completion_rate': round(completion_rate, 2)
            })

        # Payment analytics
        payment_stats = {
            'total_revenue': Payment.objects.filter(status='successful').aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'monthly_revenue': Payment.objects.filter(
                status='successful',
                created_at__gte=timezone.now() - timedelta(days=30)
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'successful_payments': Payment.objects.filter(status='successful').count(),
            'failed_payments': Payment.objects.filter(status='failed').count(),
        }

        context = {
            'title': 'Analytics',
            'user_stats': user_stats,
            'course_stats': course_stats,
            'payment_stats': payment_stats,
        }
        return render(request, 'admin/analytics.html', context)

    def user_management_view(self, request):
        """User management view with filtering."""
        from django.db.models import Q
        
        # Get filter parameters
        user_type = request.GET.get('type', 'all')
        search = request.GET.get('search', '')
        
        users = User.objects.all()
        
        # Apply filters
        if user_type == 'paid':
            users = users.filter(is_paid_user=True)
        elif user_type == 'trial':
            users = users.filter(is_paid_user=False, trial_end_date__gt=timezone.now())
        elif user_type == 'expired':
            users = users.filter(is_paid_user=False, trial_end_date__lte=timezone.now())
        
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        users = users.order_by('-date_joined')[:100]  # Limit for performance
        
        context = {
            'title': 'User Management',
            'users': users,
            'user_type': user_type,
            'search': search,
        }
        return render(request, 'admin/user_management.html', context)

    def course_management_view(self, request):
        """Course management overview."""
        context = {
            'title': 'Course Management',
            'roadmaps': Roadmap.objects.filter(is_active=True).prefetch_related('rooms'),
            'total_sections': Section.objects.filter(is_active=True).count(),
            'total_questions': Question.objects.filter(is_active=True).count(),
            'recent_completions': RoomCompletion.objects.filter(is_completed=True).order_by('-completed_at')[:10],
        }
        return render(request, 'admin/course_management.html', context)

    def export_data_view(self, request):
        """Export data in various formats."""
        import csv
        from django.http import HttpResponse
        
        export_type = request.GET.get('type', 'users')
        
        if export_type == 'users':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="users.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Is Paid', 'Trial End', 'Date Joined'])
            
            for user in User.objects.all():
                writer.writerow([
                    user.username,
                    user.email,
                    user.first_name,
                    user.last_name,
                    user.is_paid_user,
                    user.trial_end_date.strftime('%Y-%m-%d') if user.trial_end_date else '',
                    user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            return response
        
        elif export_type == 'completions':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="completions.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['User', 'Room', 'Completed', 'Score', 'Date'])
            
            for completion in RoomCompletion.objects.select_related('user', 'room').all():
                writer.writerow([
                    completion.user.username,
                    completion.room.title,
                    completion.is_completed,
                    completion.final_exam_score or '',
                    completion.completed_at.strftime('%Y-%m-%d %H:%M:%S') if completion.completed_at else ''
                ])
            
            return response
        
        # Default: show export options
        context = {
            'title': 'Export Data',
        }
        return render(request, 'admin/export_data.html', context)


# Create custom admin site instance
admin_site = CustomAdminSite(name='custom_admin')

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
admin_site.register(Enrollment, EnrollmentAdmin)
admin_site.register(Payment, PaymentAdmin)
