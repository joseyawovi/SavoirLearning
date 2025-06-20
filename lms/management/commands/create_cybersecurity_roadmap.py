
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lms.models import Roadmap, Room, Section, Question, RoadmapEnrollment, QuestionChoice
import random

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
                    {'title': 'Introduction to Cybersecurity', 'description': 'Overview of cybersecurity field and career paths'},
                    {'title': 'CIA Triad', 'description': 'Confidentiality, Integrity, and Availability principles'},
                    {'title': 'Security Frameworks', 'description': 'NIST, ISO 27001, and other security standards'}
                ]
            },
            {
                'title': 'Network Security',
                'description': 'Understand network vulnerabilities, secure network design, and network monitoring techniques.',
                'sections': [
                    {'title': 'Network Protocols', 'description': 'TCP/IP, DNS, HTTP/HTTPS security considerations'},
                    {'title': 'Firewalls and IDS', 'description': 'Network security devices and configurations'},
                    {'title': 'VPNs and Encryption', 'description': 'Secure communication channels and encryption methods'}
                ]
            },
            {
                'title': 'Threat Intelligence',
                'description': 'Learn about common threats, attack vectors, and how to analyze and respond to security incidents.',
                'sections': [
                    {'title': 'Common Attack Types', 'description': 'Malware, phishing, social engineering, and DDoS'},
                    {'title': 'Threat Hunting', 'description': 'Proactive threat detection and analysis techniques'},
                    {'title': 'Incident Response', 'description': 'Security incident handling and recovery procedures'}
                ]
            },
            {
                'title': 'Vulnerability Management',
                'description': 'Master vulnerability assessment, penetration testing, and security auditing techniques.',
                'sections': [
                    {'title': 'Vulnerability Scanning', 'description': 'Automated tools and manual testing techniques'},
                    {'title': 'Penetration Testing', 'description': 'Ethical hacking methodologies and tools'},
                    {'title': 'Security Auditing', 'description': 'Compliance checking and security assessments'}
                ]
            },
            {
                'title': 'Security Operations',
                'description': 'Learn about SOC operations, SIEM systems, and continuous security monitoring.',
                'sections': [
                    {'title': 'SOC Operations', 'description': 'Security Operations Center roles and responsibilities'},
                    {'title': 'SIEM and Logging', 'description': 'Log analysis and security information management'},
                    {'title': 'Continuous Monitoring', 'description': 'Real-time security monitoring and alerting'}
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
                        'description': section_data['description'],
                        'content': f"<h2>{section_data['title']}</h2><p>{section_data['description']}</p><p>This section covers essential concepts and practical applications in cybersecurity.</p>",
                        'order': j,
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'    Created section: {section.title}')

                    # Create quiz questions for each section
                    questions_data = [
                        {
                            'text': f'What is the primary focus of {section_data["title"]}?',
                            'choices': [
                                {'text': section_data['description'], 'is_correct': True},
                                {'text': 'Data encryption methods', 'is_correct': False},
                                {'text': 'Hardware maintenance', 'is_correct': False},
                                {'text': 'Software development', 'is_correct': False}
                            ]
                        },
                        {
                            'text': f'Which skill is most important for {section_data["title"]}?',
                            'choices': [
                                {'text': 'Technical analysis', 'is_correct': True},
                                {'text': 'Graphic design', 'is_correct': False},
                                {'text': 'Marketing', 'is_correct': False},
                                {'text': 'Sales', 'is_correct': False}
                            ]
                        }
                    ]

                    for q_data in questions_data:
                        question = Question.objects.create(
                            section=section,
                            text=q_data['text'],
                            question_type='multiple_choice',
                            order=len(questions_data)
                        )

                        for choice_data in q_data['choices']:
                            QuestionChoice.objects.create(
                                question=question,
                                text=choice_data['text'],
                                is_correct=choice_data['is_correct']
                            )

            # Create final exam for the room
            final_exam, created = Section.objects.get_or_create(
                title=f'{room.title} - Final Exam',
                room=room,
                defaults={
                    'description': f'Final assessment for {room.title}',
                    'content': f'<h2>Final Exam: {room.title}</h2><p>Test your knowledge of all concepts covered in this room.</p>',
                    'is_final_exam': True,
                    'order': 999,
                    'is_active': True
                }
            )

        # Enroll admin user in the roadmap
        try:
            admin_user = User.objects.get(username='admin')
            enrollment, created = RoadmapEnrollment.objects.get_or_create(
                user=admin_user,
                roadmap=roadmap
            )
            self.stdout.write(f'Enrolled admin user in {roadmap.title}')
        except User.DoesNotExist:
            self.stdout.write('Admin user not found, skipping enrollment')

        self.stdout.write(self.style.SUCCESS(f'{roadmap.title} roadmap created successfully!'))
