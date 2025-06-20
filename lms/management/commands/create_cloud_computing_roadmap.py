
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lms.models import Roadmap, Room, Section, Question, Enrollment
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create Cloud Computing roadmap with 5 rooms and comprehensive content'

    def handle(self, *args, **options):
        self.stdout.write('Creating Cloud Computing roadmap...')

        # Create roadmap
        roadmap, created = Roadmap.objects.get_or_create(
            title='Cloud Computing Mastery',
            defaults={
                'description': 'Master cloud computing concepts, services, and deployment strategies across major cloud platforms including AWS, Azure, and Google Cloud.',
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
                'title': 'Cloud Fundamentals',
                'description': 'Learn the basic concepts of cloud computing, service models, and deployment models.',
                'sections': [
                    {'title': 'Introduction to Cloud Computing', 'description': 'History, benefits, and key characteristics of cloud computing'},
                    {'title': 'Service Models (IaaS, PaaS, SaaS)', 'description': 'Understanding different cloud service delivery models'},
                    {'title': 'Deployment Models', 'description': 'Public, private, hybrid, and multi-cloud strategies'}
                ]
            },
            {
                'title': 'AWS Essentials',
                'description': 'Master Amazon Web Services core services, architecture, and best practices.',
                'sections': [
                    {'title': 'AWS Core Services', 'description': 'EC2, S3, RDS, and other fundamental AWS services'},
                    {'title': 'AWS Networking', 'description': 'VPC, security groups, and network architecture'},
                    {'title': 'AWS Security', 'description': 'IAM, security best practices, and compliance'}
                ]
            },
            {
                'title': 'Azure Platform',
                'description': 'Explore Microsoft Azure services, Azure Active Directory, and enterprise integration.',
                'sections': [
                    {'title': 'Azure Core Services', 'description': 'Virtual machines, storage, and Azure SQL Database'},
                    {'title': 'Azure Active Directory', 'description': 'Identity management and authentication services'},
                    {'title': 'Azure DevOps', 'description': 'CI/CD pipelines and development tools'}
                ]
            },
            {
                'title': 'Container Orchestration',
                'description': 'Learn Docker, Kubernetes, and container management in the cloud.',
                'sections': [
                    {'title': 'Docker Fundamentals', 'description': 'Containerization concepts and Docker basics'},
                    {'title': 'Kubernetes Architecture', 'description': 'Container orchestration and cluster management'},
                    {'title': 'Cloud-Native Development', 'description': 'Microservices and serverless architectures'}
                ]
            },
            {
                'title': 'Cloud Operations',
                'description': 'Master monitoring, automation, and cost optimization in cloud environments.',
                'sections': [
                    {'title': 'Cloud Monitoring', 'description': 'Performance monitoring and alerting systems'},
                    {'title': 'Infrastructure as Code', 'description': 'Terraform, CloudFormation, and automation'},
                    {'title': 'Cost Optimization', 'description': 'Cloud cost management and optimization strategies'}
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
                        'content': f"<h2>{section_data['title']}</h2><p>{section_data['description']}</p><p>This section provides comprehensive coverage of cloud computing concepts and practical implementation.</p>",
                        'order': j,
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'    Created section: {section.title}')

                    # Create quiz questions for each section
                    questions_data = [
                        {
                            'prompt': f'What is the main benefit of {section_data["title"]}?',
                            'correct_answer': 'scalability and flexibility',
                            'placeholder_hint': 'scalability and _______'
                        },
                        {
                            'prompt': f'Which concept is central to {section_data["title"]}?',
                            'correct_answer': section_data['description'].split()[0].lower(),
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
                    'prompt': f'What are the key concepts covered in {room.title}?',
                    'correct_answer': 'cloud computing fundamentals',
                    'placeholder_hint': 'cloud _______ fundamentals'
                },
                {
                    'prompt': f'How does {room.title} benefit organizations?',
                    'correct_answer': 'improved efficiency and scalability',
                    'placeholder_hint': 'improved _______ and _______'
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
