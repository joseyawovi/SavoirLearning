from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lms.models import Roadmap, Room, Section, Question, Enrollment
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create Cybersecurity Fundamentals roadmap with 5 rooms and comprehensive content'

    def handle(self, *args, **options):
        self.stdout.write('Creating Cybersecurity Fundamentals roadmap...')

        # Create roadmap
        roadmap, created = Roadmap.objects.get_or_create(
            title='Cybersecurity Fundamentals',
            defaults={
                'description': 'Master the essential concepts of cybersecurity, from basic security principles to advanced threat detection and prevention techniques.',
                'is_active': True
            }
        )

        if created:
            self.stdout.write(f'Created roadmap: {roadmap.title}')
        else:
            self.stdout.write(f'Roadmap already exists: {roadmap.title}')

        # Define rooms
        rooms_data = [
            {
                'title': 'Security Fundamentals',
                'description': 'Learn the basic principles of information security including CIA triad, threat landscape, and security frameworks.',
                'sections': [
                    {'title': 'Introduction to Cybersecurity'},
                    {'title': 'CIA Triad'},
                    {'title': 'Security Frameworks'}
                ]
            },
            {
                'title': 'Network Security',
                'description': 'Understand network vulnerabilities, secure network design, and network monitoring techniques.',
                'sections': [
                    {'title': 'Network Protocols'},
                    {'title': 'Firewalls and IDS'},
                    {'title': 'VPNs and Encryption'}
                ]
            },
            {
                'title': 'Threat Intelligence',
                'description': 'Learn about common threats, attack vectors, and how to analyze and respond to security incidents.',
                'sections': [
                    {'title': 'Common Attack Types'},
                    {'title': 'Threat Hunting'},
                    {'title': 'Incident Response'}
                ]
            },
            {
                'title': 'Vulnerability Management',
                'description': 'Master vulnerability assessment, penetration testing, and security auditing techniques.',
                'sections': [
                    {'title': 'Vulnerability Scanning'},
                    {'title': 'Penetration Testing'},
                    {'title': 'Security Auditing'}
                ]
            },
            {
                'title': 'Security Operations',
                'description': 'Learn about SOC operations, SIEM systems, and continuous security monitoring.',
                'sections': [
                    {'title': 'SOC Operations'},
                    {'title': 'SIEM and Logging'},
                    {'title': 'Continuous Monitoring'}
                ]
            }
        ]

        # Create rooms and sections
        for i, room_data in enumerate(rooms_data, 1):
            room, created = Room.objects.get_or_create(
                title=room_data['title'],
                roadmap=roadmap,
                defaults={
                    'description': room_data['description'],
                    'order': i,
                    'is_active': True
                }
            )

            if created:
                self.stdout.write(f'  Created room: {room.title}')

            # Create sections for this room
            for j, section_data in enumerate(room_data['sections'], 1):
                section, created = Section.objects.get_or_create(
                    title=section_data['title'],
                    room=room,
                    defaults={
                        'content': f"<h2>{section_data['title']}</h2><p>This section covers essential concepts and practical applications in cybersecurity.</p>",
                        'order': j,
                        'is_active': True
                    }
                )

                if created:
                    self.stdout.write(f'    Created section: {section.title}')

                    # Create quiz questions for each section
                    # Create quiz questions for each section
                    questions_data = [
                        {
                            'prompt': f'What is the main benefit of {section_data["title"]}?',
                            'correct_answer': 'enhanced security posture',
                            'placeholder_hint': 'enhanced _______ posture'
                        },
                        {
                            'prompt': f'Which concept is central to {section_data["title"]}?',
                            'correct_answer': section_data['title'].split()[0].lower(),
                            'placeholder_hint': '_______ concept'
                        }
                    ]

                    for i, q_data in enumerate(questions_data, 1):
                        Question.objects.create(
                            section=section,
                            prompt=q_data['prompt'],
                            correct_answer=q_data['correct_answer'],
                            placeholder_hint=q_data['placeholder_hint'],
                            question_type='section',
                            order=i
                        )

            # Create final exam questions for the room
            final_questions = [
                {
                    'prompt': f'What are the key security principles covered in {room.title}?',
                    'correct_answer': 'confidentiality integrity availability',
                    'placeholder_hint': 'confidentiality _______ _______'
                },
                {
                    'prompt': f'How does {room.title} help protect organizations?',
                    'correct_answer': 'threat prevention and risk mitigation',
                    'placeholder_hint': 'threat _______ and risk _______'
                }
            ]

            for i, q_data in enumerate(final_questions, 1):
                Question.objects.create(
                    room=room,
                    prompt=q_data['prompt'],
                    correct_answer=q_data['correct_answer'],
                    placeholder_hint=q_data['placeholder_hint'],
                    question_type='final',
                    order=i
                )

        # Enroll admin user in the roadmap
        try:
            admin_user = User.objects.get(username='admin')
            enrollment, created = Enrollment.objects.get_or_create(
                user=admin_user,
                roadmap=roadmap
            )
            self.stdout.write(f'Enrolled admin user in {roadmap.title}')
        except User.DoesNotExist:
            self.stdout.write('Admin user not found, skipping enrollment')

        self.stdout.write(self.style.SUCCESS(f'{roadmap.title} roadmap created successfully!'))