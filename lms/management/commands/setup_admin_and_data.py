
"""
Management command to create admin user and populate mock data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from lms.models import (
    User, Roadmap, Room, Section, Question, 
    SectionCompletion, RoomCompletion, Certificate, Payment
)


class Command(BaseCommand):
    help = 'Create admin user and populate database with mock data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@savoirplus.com',
            help='Admin email (default: admin@savoirplus.com)'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Admin password (default: admin123)'
        )

    def handle(self, *args, **options):
        # Create admin user
        User = get_user_model()
        admin_username = options['admin_username']
        admin_email = options['admin_email']
        admin_password = options['admin_password']

        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{admin_username}" already exists.')
            )
        else:
            admin_user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                first_name='Admin',
                last_name='User',
                is_paid_user=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user: {admin_username}')
            )

        # Create mock data
        self.create_mock_data()
        
        self.stdout.write(
            self.style.SUCCESS('Mock data created successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Admin login: {admin_username} / {admin_password}')
        )

    def create_mock_data(self):
        # Create roadmaps
        cybersec_roadmap = Roadmap.objects.get_or_create(
            title='Cybersecurity Fundamentals',
            defaults={
                'title_fr': 'Fondamentaux de la Cybersécurité',
                'description': 'Complete cybersecurity learning path covering all essential topics.',
                'description_fr': 'Parcours d\'apprentissage complet couvrant tous les sujets essentiels.',
                'is_active': True
            }
        )[0]

        web_roadmap = Roadmap.objects.get_or_create(
            title='Web Application Security',
            defaults={
                'title_fr': 'Sécurité des Applications Web',
                'description': 'Learn to secure web applications and find vulnerabilities.',
                'description_fr': 'Apprenez à sécuriser les applications web et à trouver les vulnérabilités.',
                'is_active': True
            }
        )[0]

        # Create rooms for cybersecurity roadmap
        intro_room = Room.objects.get_or_create(
            title='Introduction to Cybersecurity',
            roadmap=cybersec_roadmap,
            defaults={
                'title_fr': 'Introduction à la Cybersécurité',
                'description': 'Learn the basics of cybersecurity, threats, and defense mechanisms.',
                'description_fr': 'Apprenez les bases de la cybersécurité, les menaces et les mécanismes de défense.',
                'order': 1,
                'is_active': True
            }
        )[0]

        network_room = Room.objects.get_or_create(
            title='Network Security',
            roadmap=cybersec_roadmap,
            defaults={
                'title_fr': 'Sécurité Réseau',
                'description': 'Understanding network protocols, attacks, and security measures.',
                'description_fr': 'Comprendre les protocoles réseau, les attaques et les mesures de sécurité.',
                'prerequisite_room': intro_room,
                'order': 2,
                'is_active': True
            }
        )[0]

        # Create rooms for web security roadmap
        web_basics_room = Room.objects.get_or_create(
            title='Web Security Basics',
            roadmap=web_roadmap,
            defaults={
                'title_fr': 'Bases de la Sécurité Web',
                'description': 'Fundamental concepts of web application security.',
                'description_fr': 'Concepts fondamentaux de la sécurité des applications web.',
                'order': 1,
                'is_active': True
            }
        )[0]

        # Create sections for intro room
        section1 = Section.objects.get_or_create(
            title='What is Cybersecurity?',
            room=intro_room,
            defaults={
                'title_fr': 'Qu\'est-ce que la Cybersécurité?',
                'content': '''
                <h3>Introduction to Cybersecurity</h3>
                <p>Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. These cyberattacks are usually aimed at accessing, changing, or destroying sensitive information; extorting money from users; or interrupting normal business processes.</p>
                
                <h4>Key Components:</h4>
                <ul>
                    <li><strong>Information Security:</strong> Protecting data integrity, confidentiality, and availability</li>
                    <li><strong>Network Security:</strong> Protecting computer networks from intrusion</li>
                    <li><strong>Application Security:</strong> Keeping software and devices free of threats</li>
                    <li><strong>Operational Security:</strong> Handling and protecting data assets</li>
                </ul>
                
                <h4>The CIA Triad:</h4>
                <p>The three pillars of cybersecurity:</p>
                <ul>
                    <li><strong>Confidentiality:</strong> Information is accessible only to authorized users</li>
                    <li><strong>Integrity:</strong> Information is accurate and complete</li>
                    <li><strong>Availability:</strong> Information is accessible when needed</li>
                </ul>
                ''',
                'content_fr': '''
                <h3>Introduction à la Cybersécurité</h3>
                <p>La cybersécurité est la pratique de protection des systèmes, réseaux et programmes contre les attaques numériques.</p>
                ''',
                'video_url': 'https://www.youtube.com/watch?v=inWWhr5tnEA',
                'order': 1,
                'is_active': True
            }
        )[0]

        section2 = Section.objects.get_or_create(
            title='Common Cyber Threats',
            room=intro_room,
            defaults={
                'title_fr': 'Menaces Cyber Communes',
                'content': '''
                <h3>Types of Cyber Threats</h3>
                <p>Understanding different types of cyber threats is crucial for effective defense.</p>
                
                <h4>Malware:</h4>
                <ul>
                    <li><strong>Virus:</strong> Self-replicating programs that attach to other files</li>
                    <li><strong>Worms:</strong> Standalone malware that spreads across networks</li>
                    <li><strong>Trojans:</strong> Malicious software disguised as legitimate programs</li>
                    <li><strong>Ransomware:</strong> Encrypts files and demands payment for decryption</li>
                </ul>
                
                <h4>Social Engineering:</h4>
                <ul>
                    <li><strong>Phishing:</strong> Fraudulent emails to steal sensitive information</li>
                    <li><strong>Spear Phishing:</strong> Targeted phishing attacks</li>
                    <li><strong>Baiting:</strong> Offering something enticing to spark curiosity</li>
                    <li><strong>Pretexting:</strong> Creating fake scenarios to gain trust</li>
                </ul>
                
                <h4>Network Attacks:</h4>
                <ul>
                    <li><strong>DDoS:</strong> Overwhelming systems with traffic</li>
                    <li><strong>Man-in-the-Middle:</strong> Intercepting communications</li>
                    <li><strong>SQL Injection:</strong> Exploiting database vulnerabilities</li>
                </ul>
                ''',
                'order': 2,
                'is_active': True
            }
        )[0]

        # Create questions for sections
        Question.objects.get_or_create(
            section=section1,
            question_type='section',
            prompt='What does CIA stand for in cybersecurity?',
            defaults={
                'prompt_fr': 'Que signifie CIA en cybersécurité?',
                'correct_answer': 'Confidentiality Integrity Availability',
                'placeholder_hint': '_______ _______ _______',
                'order': 1,
                'is_active': True
            }
        )

        Question.objects.get_or_create(
            section=section1,
            question_type='section',
            prompt='Which pillar ensures that information is accessible only to authorized users?',
            defaults={
                'correct_answer': 'Confidentiality',
                'placeholder_hint': '_______',
                'order': 2,
                'is_active': True
            }
        )

        Question.objects.get_or_create(
            section=section2,
            question_type='section',
            prompt='What type of malware encrypts files and demands payment?',
            defaults={
                'correct_answer': 'Ransomware',
                'placeholder_hint': '_______',
                'order': 1,
                'is_active': True
            }
        )

        # Create final exam questions for intro room
        Question.objects.get_or_create(
            room=intro_room,
            question_type='final',
            prompt='Name the three pillars of the CIA triad (separate with spaces)',
            defaults={
                'correct_answer': 'Confidentiality Integrity Availability',
                'placeholder_hint': '_______ _______ _______',
                'order': 1,
                'is_active': True
            }
        )

        Question.objects.get_or_create(
            room=intro_room,
            question_type='final',
            prompt='What is the practice of creating fake scenarios to gain trust called?',
            defaults={
                'correct_answer': 'Pretexting',
                'placeholder_hint': '_______',
                'order': 2,
                'is_active': True
            }
        )

        # Create sample users
        trial_user = User.objects.get_or_create(
            username='trial_user',
            defaults={
                'email': 'trial@example.com',
                'first_name': 'Trial',
                'last_name': 'User',
                'is_paid_user': False
            }
        )[0]
        trial_user.set_password('password123')
        trial_user.save()

        premium_user = User.objects.get_or_create(
            username='premium_user',
            defaults={
                'email': 'premium@example.com',
                'first_name': 'Premium',
                'last_name': 'User',
                'is_paid_user': True
            }
        )[0]
        premium_user.set_password('password123')
        premium_user.save()

        # Create some sample progress
        SectionCompletion.objects.get_or_create(
            user=premium_user,
            section=section1,
            defaults={
                'is_completed': True,
                'completed_at': timezone.now()
            }
        )

        # Create sample payment
        Payment.objects.get_or_create(
            transaction_id='SAMPLE_TXN_001',
            defaults={
                'user': premium_user,
                'amount': 15000,
                'currency': 'XOF',
                'payment_method': 'flutterwave',
                'status': 'successful'
            }
        )

        self.stdout.write('Created mock roadmaps, rooms, sections, questions, and users')
