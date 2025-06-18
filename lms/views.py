"""
Views for Savoir+ LMS.
"""
import uuid
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import timedelta
import csv
from .models import (
    User, Roadmap, Room, Section, Question, UserAnswer,
    SectionCompletion, RoomCompletion, Certificate, Payment, Enrollment
)
from .forms import UserRegistrationForm, QuizAnswerForm
from .utils import generate_certificate_pdf


def home(request):
    """Home page view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    roadmaps = Roadmap.objects.filter(is_active=True)
    return render(request, 'lms/home.html', {'roadmaps': roadmaps})


@login_required  
def enroll_roadmap(request, roadmap_id):
    """Enroll user in a specific roadmap."""
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, is_active=True)
    
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        roadmap=roadmap
    )
    
    if created:
        messages.success(request, f'Successfully enrolled in {roadmap.title}!')
    else:
        messages.info(request, f'You are already enrolled in {roadmap.title}.')
    
    return redirect('dashboard')


def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Welcome to Savoir+! Your 15-day trial has started.'))
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    """User dashboard showing enrolled roadmaps and progress."""
    # Get user's enrolled roadmaps only
    enrolled_roadmaps = Enrollment.objects.filter(
        user=request.user, is_active=True
    ).select_related('roadmap').prefetch_related('roadmap__rooms')
    
    # If no enrollments, auto-enroll in all active roadmaps for trial users
    if not enrolled_roadmaps.exists():
        active_roadmaps = Roadmap.objects.filter(is_active=True)
        for roadmap in active_roadmaps:
            Enrollment.objects.get_or_create(
                user=request.user,
                roadmap=roadmap
            )
        enrolled_roadmaps = Enrollment.objects.filter(
            user=request.user, is_active=True
        ).select_related('roadmap').prefetch_related('roadmap__rooms')
    
    # Get roadmaps from enrollments
    roadmaps = [enrollment.roadmap for enrollment in enrolled_roadmaps]
    
    # Get user's completed rooms
    completed_rooms = RoomCompletion.objects.filter(
        user=request.user, is_completed=True
    ).values_list('room_id', flat=True)
    
    # Get user's certificates
    certificates = Certificate.objects.filter(user=request.user, is_valid=True)
    
    # Calculate overall progress only for enrolled courses
    enrolled_rooms = Room.objects.filter(
        roadmap__in=roadmaps, is_active=True
    )
    total_rooms = enrolled_rooms.count()
    completed_count = len([room_id for room_id in completed_rooms if room_id in enrolled_rooms.values_list('id', flat=True)])
    overall_progress = (completed_count / total_rooms * 100) if total_rooms > 0 else 0
    
    # Get recent section completions for activity feed
    recent_completions = SectionCompletion.objects.filter(
        user=request.user, is_completed=True
    ).select_related('section').order_by('-completed_at')[:5]
    
    # Organize roadmap data with progress
    roadmap_data = []
    for roadmap in roadmaps:
        rooms = roadmap.rooms.filter(is_active=True).order_by('order')
        rooms_data = []
        roadmap_completed = 0
        
        for room in rooms:
            is_accessible = room.is_accessible_by_user(request.user)
            is_completed = room.id in completed_rooms
            
            if is_completed:
                roadmap_completed += 1
            
            # Get sections progress for this room
            sections = room.sections.filter(is_active=True)
            completed_sections = SectionCompletion.objects.filter(
                user=request.user, section__in=sections, is_completed=True
            ).count()
            
            sections_progress = (completed_sections / sections.count() * 100) if sections.count() > 0 else 0
            
            rooms_data.append({
                'room': room,
                'is_accessible': is_accessible,
                'is_completed': is_completed,
                'sections_progress': sections_progress,
                'sections_total': sections.count(),
                'sections_completed': completed_sections,
            })
        
        roadmap_progress = (roadmap_completed / rooms.count() * 100) if rooms.count() > 0 else 0
        
        # Add user progress calculation for each roadmap
        roadmap.user_progress = roadmap_progress
        
        # Calculate stroke-dashoffset for SVG progress circle
        stroke_dashoffset = 175.93 - (roadmap_progress / 100 * 175.93)
        
        roadmap_data.append({
            'roadmap': roadmap,
            'rooms': rooms_data,
            'progress': roadmap_progress,
            'completed_rooms': roadmap_completed,
            'total_rooms': rooms.count(),
            'stroke_dashoffset': stroke_dashoffset,
        })
    
    context = {
        'roadmaps': roadmap_data,  # Changed key name to match template
        'roadmap_data': roadmap_data,
        'user': request.user,
        'certificates': certificates,
        'certificates_count': certificates.count(),
        'overall_progress': overall_progress,
        'completed_rooms': completed_count,  # Changed key name to match template
        'total_completed_rooms': completed_count,
        'total_rooms': total_rooms,
        'recent_completions': recent_completions,
    }
    return render(request, 'lms/dashboard.html', context)


@login_required
def roadmap_detail(request, roadmap_id):
    """Detailed view of a specific roadmap."""
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, is_active=True)
    
    # Get user's completed rooms
    completed_rooms = RoomCompletion.objects.filter(
        user=request.user, is_completed=True
    ).values_list('room_id', flat=True)
    
    rooms_data = []
    total_rooms = 0
    completed_count = 0
    
    for room in roadmap.rooms.filter(is_active=True).order_by('order'):
        is_accessible = room.is_accessible_by_user(request.user)
        is_completed = room.id in completed_rooms
        
        if is_completed:
            completed_count += 1
        total_rooms += 1
        
        # Get sections count and completion
        sections = room.sections.filter(is_active=True)
        completed_sections = SectionCompletion.objects.filter(
            user=request.user, section__in=sections, is_completed=True
        ).count()
        
        rooms_data.append({
            'room': room,
            'is_accessible': is_accessible,
            'is_completed': is_completed,
            'total_sections': sections.count(),
            'completed_sections': completed_sections,
        })
    
    # Calculate overall progress
    user_progress = (completed_count / total_rooms * 100) if total_rooms > 0 else 0
    
    # Calculate progress circle offset (circumference = 2 * π * r = 2 * π * 56 = 351.86)
    progress_offset = 351.86 - (user_progress / 100 * 351.86)
    
    context = {
        'roadmap': roadmap,
        'rooms': rooms_data,
        'user_progress': user_progress,
        'progress_offset': progress_offset,
        'total_rooms': total_rooms,
        'completed_count': completed_count,
    }
    return render(request, 'lms/roadmap_detail.html', context)


@login_required
def room_detail(request, room_id):
    """Detailed view of a room with sections."""
    room = get_object_or_404(Room, id=room_id, is_active=True)
    
    # Check if user can access this room
    if not room.is_accessible_by_user(request.user):
        messages.error(request, _('You need to complete the prerequisite room first.'))
        return redirect('dashboard')
    
    sections = room.sections.filter(is_active=True).order_by('order')
    
    # Get user's section completions
    section_completions = SectionCompletion.objects.filter(
        user=request.user, section__in=sections
    )
    completed_section_ids = {sc.section_id for sc in section_completions if sc.is_completed}
    
    # Check section accessibility
    sections_data = []
    for section in sections:
        is_accessible = section.is_accessible_by_user(request.user)
        is_completed = section.id in completed_section_ids
        sections_data.append({
            'section': section,
            'is_accessible': is_accessible,
            'is_completed': is_completed,
        })
    
    # Check if all sections are completed (for final exam access)
    all_sections_completed = len(completed_section_ids) == sections.count()
    
    # Get final exam questions
    final_questions = room.final_questions.filter(is_active=True).order_by('order')
    
    # Check if user has completed final exam
    room_completion = RoomCompletion.objects.filter(user=request.user, room=room).first()
    
    context = {
        'room': room,
        'sections': sections,
        'sections_data': sections_data,
        'completed_section_ids': completed_section_ids,
        'all_sections_completed': all_sections_completed,
        'final_questions': final_questions,
        'room_completion': room_completion,
        'user': request.user,
    }
    return render(request, 'lms/room_detail.html', context)


@login_required
def section_detail(request, section_id):
    """Detailed view of a section with content and quiz."""
    section = get_object_or_404(Section, id=section_id, is_active=True)
    
    # Check if user can access this section
    if not section.is_accessible_by_user(request.user):
        messages.error(request, _('You need to complete the previous sections first.'))
        return redirect('room_detail', room_id=section.room.id)
    
    # Get section questions
    questions = section.questions.filter(is_active=True).order_by('order')
    
    # Get user's answers for this section
    user_answers = UserAnswer.objects.filter(
        user=request.user, question__in=questions
    )
    answer_dict = {ua.question_id: ua for ua in user_answers}
    
    # Check if section is completed
    section_completion = SectionCompletion.objects.filter(
        user=request.user, section=section
    ).first()
    
    # Create section completion if it doesn't exist but should be completed
    if not section_completion:
        section_completion = SectionCompletion.objects.create(
            user=request.user,
            section=section,
            is_completed=False
        )
    
    # Prepare questions with user answers
    questions_data = []
    all_questions_answered_correctly = True
    
    for question in questions:
        user_answer = answer_dict.get(question.id)
        questions_data.append({
            'question': question,
            'user_answer': user_answer,
        })
        
        # Check if all questions are answered correctly
        if not user_answer or not user_answer.is_correct:
            all_questions_answered_correctly = False
    
    # Auto-complete section if no questions exist (content-only section)
    if not questions and not section_completion.is_completed:
        section_completion.is_completed = True
        section_completion.completed_at = timezone.now()
        section_completion.save()
    
    # Auto-complete section if all questions are answered correctly
    elif questions and all_questions_answered_correctly and not section_completion.is_completed:
        section_completion.is_completed = True
        section_completion.completed_at = timezone.now()
        section_completion.save()
    
    # Get next section for navigation
    next_section = Section.objects.filter(
        room=section.room,
        is_active=True,
        order__gt=section.order
    ).first()
    
    # If next section exists, check if it's accessible
    if next_section and not next_section.is_accessible_by_user(request.user):
        next_section = None
    
    context = {
        'section': section,
        'questions': questions,
        'questions_data': questions_data,
        'section_completion': section_completion,
        'all_questions_answered': len(user_answers) == len(questions),
        'all_questions_correct': all_questions_answered_correctly,
        'answered_questions': user_answers,
        'next_section': next_section,
        'user': request.user,
    }
    return render(request, 'lms/section_detail.html', context)


@login_required
@require_POST
def submit_quiz_answer(request, question_id):
    """Submit an answer to a quiz question."""
    question = get_object_or_404(Question, id=question_id, is_active=True)
    
    # Check if user can access quizzes
    if not request.user.can_access_quizzes:
        return JsonResponse({
            'success': False,
            'error': _('Quiz access requires a premium subscription.')
        })
    
    user_answer_text = request.POST.get('answer', '').strip()
    
    if not user_answer_text:
        return JsonResponse({
            'success': False,
            'error': _('Please provide an answer.')
        })
    
    # Check if answer is correct
    is_correct = question.check_answer(user_answer_text)
    
    # Save or update user answer
    user_answer, created = UserAnswer.objects.update_or_create(
        user=request.user,
        question=question,
        defaults={
            'answer': user_answer_text,
            'is_correct': is_correct,
        }
    )
    
    # Initialize response data
    response_data = {
        'success': True,
        'is_correct': is_correct,
        'correct': is_correct,  # Add this field for backward compatibility
        'message': _('Correct!') if is_correct else _('Incorrect. Try again.')
    }
    
    # If this is a section question, check if all section questions are answered correctly
    if question.section:
        section_questions = question.section.questions.filter(is_active=True)
        section_answers = UserAnswer.objects.filter(
            user=request.user,
            question__in=section_questions
        )
        
        # Check if all questions are answered correctly
        all_correct = (section_answers.count() == section_questions.count() and
                      all(answer.is_correct for answer in section_answers))
        
        if all_correct:
            # Mark section as completed
            section_completion, created = SectionCompletion.objects.update_or_create(
                user=request.user,
                section=question.section,
                defaults={
                    'is_completed': True,
                    'completed_at': timezone.now(),
                }
            )
            
            # Add section completion status to response
            response_data['section_completed'] = True
            response_data['completion_message'] = _('Section completed! Great job!')
            
            # Check if this completed all sections in the room to unlock next room
            room = question.section.room
            room_sections = room.sections.filter(is_active=True)
            completed_sections = SectionCompletion.objects.filter(
                user=request.user,
                section__in=room_sections,
                is_completed=True
            ).count()
            
            # If all sections completed, create or update room progress tracking
            if completed_sections == room_sections.count():
                RoomCompletion.objects.get_or_create(
                    user=request.user,
                    room=room,
                    defaults={'is_completed': False}  # Still need final exam
                )
    
    return JsonResponse(response_data)


@login_required
def final_exam(request, room_id):
    """Display or submit final exam."""
    room = get_object_or_404(Room, id=room_id, is_active=True)
    
    if request.method == 'GET':
        # Display the final exam form
        # Check if user can access quizzes
        if not request.user.can_access_quizzes:
            messages.error(request, _('Final exam access requires a premium subscription.'))
            return redirect('room_detail', room_id=room_id)
        
        # Check if all sections are completed
        sections = room.sections.filter(is_active=True)
        completed_sections = SectionCompletion.objects.filter(
            user=request.user, section__in=sections, is_completed=True
        ).count()
        
        if completed_sections != sections.count():
            messages.error(request, _('You must complete all sections before taking the final exam.'))
            return redirect('room_detail', room_id=room_id)
        
        # Get final exam questions
        final_questions = room.final_questions.filter(is_active=True).order_by('order')
        
        # Get user's previous answers if any
        user_answers = UserAnswer.objects.filter(
            user=request.user, question__in=final_questions
        )
        answer_dict = {ua.question_id: ua for ua in user_answers}
        
        context = {
            'room': room,
            'final_questions': final_questions,
            'user_answers': answer_dict,
        }
        return render(request, 'lms/final_exam.html', context)
    
    elif request.method == 'POST':
        return submit_final_exam_answers(request, room_id)


@login_required
@require_POST  
def submit_final_exam_answers(request, room_id):
    """Submit final exam answers."""
    room = get_object_or_404(Room, id=room_id, is_active=True)
    
    # Check if user can access quizzes
    if not request.user.can_access_quizzes:
        messages.error(request, _('Final exam access requires a premium subscription.'))
        return redirect('room_detail', room_id=room_id)
    
    # Check if all sections are completed
    sections = room.sections.filter(is_active=True)
    completed_sections = SectionCompletion.objects.filter(
        user=request.user, section__in=sections, is_completed=True
    ).count()
    
    if completed_sections != sections.count():
        messages.error(request, _('You must complete all sections before taking the final exam.'))
        return redirect('room_detail', room_id=room_id)
    
    final_questions = room.final_questions.filter(is_active=True)
    
    correct_answers = 0
    total_questions = final_questions.count()
    
    # Process each answer
    for question in final_questions:
        answer_key = f'question_{question.id}'
        user_answer_text = request.POST.get(answer_key, '').strip()
        
        if user_answer_text:
            is_correct = question.check_answer(user_answer_text)
            
            # Save answer
            UserAnswer.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={
                    'answer': user_answer_text,
                    'is_correct': is_correct,
                }
            )
            
            if is_correct:
                correct_answers += 1
    
    # Calculate score
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Mark room as completed if score >= 70%
    is_passed = score >= 70
    
    room_completion, created = RoomCompletion.objects.update_or_create(
        user=request.user,
        room=room,
        defaults={
            'is_completed': is_passed,
            'completed_at': timezone.now() if is_passed else None,
            'final_exam_score': score,
        }
    )
    
    if is_passed:
        # Generate certificate
        certificate, created = Certificate.objects.get_or_create(
            user=request.user,
            room=room
        )
        
        messages.success(request, _('Congratulations! You passed the final exam. Your certificate is ready for download.'))
    else:
        messages.warning(request, _('You scored {score}%. You need at least 70% to pass. Please try again.').format(score=score))
    
    return redirect('room_detail', room_id=room_id)


@login_required
def download_certificate(request, certificate_id):
    """Download certificate PDF."""
    certificate = get_object_or_404(
        Certificate,
        certificate_id=certificate_id,
        user=request.user,
        is_valid=True
    )
    
    # Generate PDF
    pdf_content = generate_certificate_pdf(certificate)
    
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.certificate_id}.pdf"'
    
    return response


def verify_certificate(request, certificate_id):
    """Public certificate verification."""
    try:
        certificate = Certificate.objects.get(
            certificate_id=certificate_id,
            is_valid=True
        )
        context = {
            'certificate': certificate,
            'is_valid': True,
        }
    except Certificate.DoesNotExist:
        context = {
            'is_valid': False,
        }
    
    return render(request, 'lms/certificate_verification.html', context)


@login_required
def upgrade_to_premium(request):
    """Upgrade to premium subscription."""
    if request.user.is_paid_user:
        messages.info(request, _('You already have a premium subscription.'))
        return redirect('dashboard')
    
    context = {
        'user': request.user,
        'flutterwave_public_key': settings.FLUTTERWAVE_PUBLIC_KEY,
    }
    return render(request, 'lms/upgrade.html', context)


@csrf_exempt
@require_POST
def payment_callback(request):
    """Handle payment callback from Flutterwave."""
    transaction_id = request.POST.get('transaction_id')
    status = request.POST.get('status')
    user_id = request.POST.get('user_id')
    
    try:
        user = User.objects.get(id=user_id)
        
        # Create or update payment record
        payment, created = Payment.objects.update_or_create(
            transaction_id=transaction_id,
            defaults={
                'user': user,
                'amount': 15000,  # Example amount in XOF
                'currency': 'XOF',
                'payment_method': 'flutterwave',
                'status': 'successful' if status == 'successful' else 'failed',
            }
        )
        
        if status == 'successful':
            # Upgrade user to premium
            user.is_paid_user = True
            user.save()
            
            return JsonResponse({'success': True, 'message': 'Payment successful'})
        
    except User.DoesNotExist:
        pass
    
    return JsonResponse({'success': False, 'message': 'Payment failed'})


# Custom Admin Views
def is_staff_or_superuser(user):
    """Check if user is staff or superuser."""
    return user.is_staff or user.is_superuser


@user_passes_test(is_staff_or_superuser)
def admin_dashboard(request):
    """Custom admin dashboard."""
    # Get statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    paid_users = User.objects.filter(is_paid_user=True).count()
    trial_users = User.objects.filter(is_paid_user=False).count()
    
    total_roadmaps = Roadmap.objects.count()
    active_roadmaps = Roadmap.objects.filter(is_active=True).count()
    total_rooms = Room.objects.count()
    total_sections = Section.objects.count()
    
    # Recent activity
    recent_users = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).order_by('-date_joined')[:5]
    
    recent_completions = RoomCompletion.objects.filter(
        completed_at__gte=timezone.now() - timedelta(days=7)
    ).select_related('user', 'room').order_by('-completed_at')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'paid_users': paid_users,
        'trial_users': trial_users,
        'total_roadmaps': total_roadmaps,
        'active_roadmaps': active_roadmaps,
        'total_rooms': total_rooms,
        'total_sections': total_sections,
        'recent_users': recent_users,
        'recent_completions': recent_completions,
    }
    
    return render(request, 'admin/custom_dashboard.html', context)


@user_passes_test(is_staff_or_superuser)
def admin_analytics(request):
    """Analytics view with detailed statistics."""
    # User statistics
    user_stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'paid_users': User.objects.filter(is_paid_user=True).count(),
        'trial_users': User.objects.filter(is_paid_user=False, is_active=True).count(),
    }
    
    # Course statistics
    course_stats = {
        'total_roadmaps': Roadmap.objects.count(),
        'active_roadmaps': Roadmap.objects.filter(is_active=True).count(),
        'total_rooms': Room.objects.count(),
        'total_sections': Section.objects.count(),
    }
    
    # Completion statistics
    completion_stats = {
        'total_completions': RoomCompletion.objects.filter(is_completed=True).count(),
        'certificates_issued': Certificate.objects.filter(is_valid=True).count(),
        'avg_completion_rate': 0,  # Calculate based on your needs
    }
    
    # Popular courses
    popular_courses = Room.objects.annotate(
        completion_count=Count('roomcompletion')
    ).order_by('-completion_count')[:5]
    
    context = {
        'user_stats': user_stats,
        'course_stats': course_stats,
        'completion_stats': completion_stats,
        'popular_courses': popular_courses,
    }
    
    return render(request, 'admin/analytics.html', context)


@user_passes_test(is_staff_or_superuser)
def admin_users(request):
    """User management view."""
    # Filter parameters
    user_type = request.GET.get('type', 'all')
    search = request.GET.get('search', '')
    
    users = User.objects.all()
    
    if user_type == 'paid':
        users = users.filter(is_paid_user=True)
    elif user_type == 'trial':
        users = users.filter(is_paid_user=False, is_active=True)
    elif user_type == 'inactive':
        users = users.filter(is_active=False)
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'user_type': user_type,
        'search': search,
    }
    
    return render(request, 'admin/user_management.html', context)


@user_passes_test(is_staff_or_superuser)
def admin_courses(request):
    """Course management view."""
    roadmaps = Roadmap.objects.prefetch_related('rooms__sections').annotate(
        room_count=Count('rooms'),
        completion_count=Count('rooms__roomcompletion')
    ).order_by('-created_at')
    
    context = {
        'roadmaps': roadmaps,
    }
    
    return render(request, 'admin/course_management.html', context)


@user_passes_test(is_staff_or_superuser)
def admin_export(request):
    """Export data view."""
    export_type = request.GET.get('type')
    
    if export_type == 'users':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Is Paid', 'Date Joined', 'Last Login'])
        
        users = User.objects.all()
        for user in users:
            writer.writerow([
                user.username,
                user.email,
                user.first_name,
                user.last_name,
                user.is_paid_user,
                user.date_joined,
                user.last_login,
            ])
        
        return response
    
    elif export_type == 'completions':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="completions.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['User', 'Room', 'Completed At', 'Final Score'])
        
        completions = RoomCompletion.objects.filter(is_completed=True).select_related('user', 'room')
        for completion in completions:
            writer.writerow([
                completion.user.username,
                completion.room.title,
                completion.completed_at,
                completion.final_exam_score,
            ])
        
        return response
    
    return render(request, 'admin/export_data.html')
