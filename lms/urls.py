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
    
    # Custom Admin Dashboard
    path('manage/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/analytics/', views.admin_analytics, name='admin_analytics'),
    path('manage/users/', views.admin_users, name='admin_users'),
    path('manage/courses/', views.admin_courses, name='admin_courses'),
    path('manage/export/', views.admin_export, name='admin_export'),
    
    # Main application
    path('dashboard/', views.dashboard, name='dashboard'),
    path('enroll/<int:roadmap_id>/', views.enroll_roadmap, name='enroll_roadmap'),
    path('roadmap/<int:roadmap_id>/', views.roadmap_detail, name='roadmap_detail'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('section/<int:section_id>/', views.section_detail, name='section_detail'),
    
    # Quiz and exam
    path('quiz/answer/<int:question_id>/', views.submit_quiz_answer, name='submit_quiz_answer'),
    path('room/<int:room_id>/final-exam/', views.submit_final_exam, name='submit_final_exam'),
    
    # Certificates
    path('certificate/<uuid:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    path('verify/<uuid:certificate_id>/', views.verify_certificate, name='verify_certificate'),
    
    # Payment
    path('upgrade/', views.upgrade_to_premium, name='upgrade_to_premium'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
]
