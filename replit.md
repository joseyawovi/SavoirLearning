# Savoir+ LMS

## Overview

Savoir+ is a comprehensive Learning Management System built with Django, inspired by TryHackMe. The platform organizes learning content into hierarchical structures: Roadmaps → Rooms → Sections. It features a freemium model with 15-day trials, multilingual support (English/French), and interactive learning components including quizzes and final assessments.

## System Architecture

### Backend Architecture
- **Framework**: Django 5.2.3 with Python 3.11
- **Database**: SQLite (default Django setup, ready for PostgreSQL migration)
- **Authentication**: Django's built-in authentication system with custom User model
- **File Storage**: Local filesystem for static assets and user uploads
- **PDF Generation**: ReportLab for certificate generation

### Frontend Architecture
- **Templates**: Django template system with Jinja2-like syntax
- **CSS Framework**: Bootstrap 5.3.0 for responsive design
- **Icons**: Font Awesome 6.0.0 for UI icons
- **JavaScript**: Vanilla JavaScript for quiz interactions and AJAX calls
- **Internationalization**: Django i18n framework for English/French support

## Key Components

### User Management
- Extended Django User model with trial tracking and payment status
- 15-day trial system with automatic expiration
- Role-based access control (trial vs. paid users)
- User registration with trial activation

### Content Structure
- **Roadmaps**: Top-level learning paths containing multiple rooms
- **Rooms**: Course-like containers with prerequisite system
- **Sections**: Individual lessons with video, text content, and quizzes
- **Questions**: Input-based quiz questions with placeholder hints

### Progress Tracking
- Section completion tracking
- Room completion tracking with final exam requirements
- Progress visualization with percentage bars
- Certificate generation upon course completion

### Access Control System
- Trial users: Video access, reading materials
- Paid users: Full access including quizzes and final exams
- Upgrade prompts and payment integration placeholders

### Multilingual Support
- Django i18n framework for UI translations
- Dual-language content fields (English/French) in models
- Language switcher in navigation
- Locale-specific URLs and content rendering

## Data Flow

### User Journey
1. User registration → Automatic trial activation (15 days)
2. Dashboard → Shows available roadmaps with progress
3. Roadmap selection → Displays rooms in sequential order
4. Room access → Sections unlock based on completion
5. Section completion → Progress tracking and next section unlock
6. Final exam → Available after all sections completed (paid users)
7. Certificate generation → PDF download upon exam completion

### Quiz System
1. Questions display with placeholder hints (e.g., "____")
2. AJAX submission for real-time feedback
3. Case-insensitive answer validation
4. Progress updates on correct answers
5. Section completion triggers on all questions answered

### Access Control Flow
1. Authentication check on all protected views
2. Trial status validation for premium features
3. Payment status determines quiz/exam access
4. Upgrade prompts for trial users on restricted content

## External Dependencies

### Python Packages
- **Django 5.2.3**: Core web framework
- **Pillow 11.2.1**: Image processing for user uploads
- **ReportLab 4.4.1**: PDF certificate generation

### Frontend Libraries (CDN)
- **Bootstrap 5.3.0**: Responsive UI framework
- **Font Awesome 6.0.0**: Icon library
- **jQuery**: AJAX interactions (if needed)

### System Dependencies
- **Python 3.11**: Runtime environment
- **SQLite**: Default database (production-ready for PostgreSQL)
- **Locale support**: For internationalization

## Deployment Strategy

### Development Environment
- **Replit Configuration**: Automated setup with `.replit` workflow
- **Package Management**: UV lock file for dependency management
- **Static Files**: Collected automatically during startup
- **Database**: SQLite with migrations applied on startup

### Production Considerations
- Database migration to PostgreSQL recommended
- Static file serving via CDN or web server
- Environment variable management for secrets
- SSL/HTTPS configuration required
- Internationalization file compilation

### Replit Deployment
- **Run Command**: `python manage.py runserver 0.0.0.0:5000`
- **Port**: 5000 (configured for Replit environment)
- **Auto-installation**: Django and ReportLab via pip
- **Static Collection**: Automated during startup

## Changelog

- June 14, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.