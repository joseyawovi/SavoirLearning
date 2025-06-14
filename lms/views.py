"""
Views for Savoir+ LMS.
"""
import uuid
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import (
    User, Roadmap, Room, Section, Question, UserAnswer,
    SectionCompletion, RoomCompletion, Certificate, Payment
)
from .forms import UserRegistrationForm, QuizAnswerForm
from .utils import generate_certificate_pdf


def home(request):
    """Home page view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    roadmaps = Roadmap.objects.filter(is_active=True)
    return render(request, 'lms/home.html', {'roadmaps': roadmaps})


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
    """User dashboard showing available roadmaps and progress."""
    roadmaps = Roadmap.objects.filter(is_active=True).prefetch_related('rooms')
    
    # Get user's completed rooms
    completed_rooms = RoomCompletion.objects.filter(
        user=request.user, is_completed=True
    ).values_list('room_id', flat=True)
    
    # Organize roadmap data with progress
    roadmap_data = []
    for roadmap in roadmaps:
        rooms_data = []
        for room in roadmap.rooms.filter(is_active=True).order_by('order'):
            is_accessible = room.is_accessible_by_user(request.user)
            is_completed = room.id in completed_rooms
            
            rooms_data.append({
                'room': room,
                'is_accessible': is_accessible,
                'is_completed': is_completed,
            })
        
        roadmap_data.append({
            'roadmap': roadmap,
            'rooms': rooms_data
        })
    
    context = {
        'roadmap_data': roadmap_data,
        'user': request.user,
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
    for room in roadmap.rooms.filter(is_active=True).order_by('order'):
        is_accessible = room.is_accessible_by_user(request.user)
        is_completed = room.id in completed_rooms
        
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
    
    context = {
        'roadmap': roadmap,
        'rooms': rooms_data,
    }
    return render(request, 'lms/roadmap.html', context)


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
    
    # Check if all sections are completed (for final exam access)
    all_sections_completed = len(completed_section_ids) == sections.count()
    
    # Get final exam questions
    final_questions = room.final_questions.filter(is_active=True).order_by('order')
    
    # Check if user has completed final exam
    room_completion = RoomCompletion.objects.filter(user=request.user, room=room).first()
    
    context = {
        'room': room,
        'sections': sections,
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
    
    # Check if user can access the room
    if not section.room.is_accessible_by_user(request.user):
        messages.error(request, _('You need to complete the prerequisite room first.'))
        return redirect('dashboard')
    
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
    
    # Prepare questions with user answers
    questions_data = []
    for question in questions:
        user_answer = answer_dict.get(question.id)
        questions_data.append({
            'question': question,
            'user_answer': user_answer,
        })
    
    context = {
        'section': section,
        'questions_data': questions_data,
        'section_completion': section_completion,
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
    
    # If this is a section question, check if all section questions are answered correctly
    if question.section:
        section_questions = question.section.questions.filter(is_active=True)
        section_answers = UserAnswer.objects.filter(
            user=request.user,
            question__in=section_questions
        )
        
        # Check if all questions are answered correctly
        if (section_answers.count() == section_questions.count() and
            all(answer.is_correct for answer in section_answers)):
            
            # Mark section as completed
            section_completion, created = SectionCompletion.objects.update_or_create(
                user=request.user,
                section=question.section,
                defaults={
                    'is_completed': True,
                    'completed_at': timezone.now(),
                }
            )
    
    return JsonResponse({
        'success': True,
        'is_correct': is_correct,
        'message': _('Correct!') if is_correct else _('Incorrect. Try again.')
    })


@login_required
@require_POST
def submit_final_exam(request, room_id):
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
