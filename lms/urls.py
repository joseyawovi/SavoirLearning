"""
URL patterns for Savoir+ LMS.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Management URLs
    path('manage/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/analytics/', views.admin_analytics, name='admin_analytics'),
    path('manage/users/', views.admin_users, name='admin_users'),
    path('manage/courses/', views.admin_courses, name='admin_courses'),
    path('manage/export/', views.admin_export, name='admin_export'),

    # Content Management URLs
    path('manage/roadmap/create/', views.admin_create_roadmap, name='admin_create_roadmap'),
    path('manage/roadmap/<int:roadmap_id>/edit/', views.admin_edit_roadmap, name='admin_edit_roadmap'),
    path('manage/room/create/', views.admin_create_room, name='admin_create_room'),
    path('manage/room/<int:room_id>/edit/', views.admin_edit_room, name='admin_edit_room'),
    path('manage/section/create/', views.admin_create_section, name='admin_create_section'),
    path('manage/section/<int:section_id>/edit/', views.admin_edit_section, name='admin_edit_section'),
    path('manage/question/create/', views.admin_create_question, name='admin_create_question'),
    path('manage/question/<int:question_id>/edit/', views.admin_edit_question, name='admin_edit_question'),

    # Main application
    path('dashboard/', views.dashboard, name='dashboard'),

    # Enrollment
    path('enroll/<int:roadmap_id>/', views.enroll_roadmap, name='enroll_roadmap'),

    # Quiz submission
    path('quiz/submit/<int:question_id>/', views.submit_quiz_answer, name='submit_quiz_answer'),
    path('final-exam/submit/<int:room_id>/', views.submit_final_exam_answers, name='submit_final_exam_answers'),

    # Custom Admin Dashboard
    path('roadmap/<int:roadmap_id>/', views.roadmap_detail, name='roadmap_detail'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('section/<int:section_id>/', views.section_detail, name='section_detail'),

    # Quiz and exam
    path('quiz/answer/<int:question_id>/', views.submit_quiz_answer, name='submit_quiz_answer'),
    path('room/<int:room_id>/final-exam/', views.final_exam, name='final_exam'),

    # Certificates
    path('certificate/<uuid:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    path('verify/<uuid:certificate_id>/', views.verify_certificate, name='verify_certificate'),

    # Payment
    path('upgrade/', views.upgrade_to_premium, name='upgrade_to_premium'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
]