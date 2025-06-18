"""
Management command to create demo data for the LMS.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lms.models import Roadmap, Room, Section, Question

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo data for the LMS'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')
        
        # Create demo roadmap
        roadmap, created = Roadmap.objects.get_or_create(
            title='Web Development Fundamentals',
            defaults={
                'title_fr': 'Fondamentaux du Développement Web',
                'description': 'Learn the basics of web development including HTML, CSS, and JavaScript.',
                'description_fr': 'Apprenez les bases du développement web incluant HTML, CSS et JavaScript.',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Created roadmap: {roadmap.title}')
        
        # Create rooms
        html_room, created = Room.objects.get_or_create(
            title='HTML Basics',
            roadmap=roadmap,
            defaults={
                'title_fr': 'Bases HTML',
                'description': 'Learn the structure and fundamentals of HTML.',
                'description_fr': 'Apprenez la structure et les fondamentaux du HTML.',
                'order': 1,
                'is_active': True
            }
        )
        
        css_room, created = Room.objects.get_or_create(
            title='CSS Styling',
            roadmap=roadmap,
            defaults={
                'title_fr': 'Style CSS',
                'description': 'Master CSS for beautiful web designs.',
                'description_fr': 'Maîtrisez CSS pour de beaux designs web.',
                'prerequisite_room': html_room,
                'order': 2,
                'is_active': True
            }
        )
        
        js_room, created = Room.objects.get_or_create(
            title='JavaScript Fundamentals',
            roadmap=roadmap,
            defaults={
                'title_fr': 'Fondamentaux JavaScript',
                'description': 'Learn JavaScript programming for interactive websites.',
                'description_fr': 'Apprenez la programmation JavaScript pour des sites interactifs.',
                'prerequisite_room': css_room,
                'order': 3,
                'is_active': True
            }
        )
        
        # Create sections for HTML room
        html_intro_section, created = Section.objects.get_or_create(
            room=html_room,
            title='Introduction to HTML',
            defaults={
                'title_fr': 'Introduction au HTML',
                'content': '''HTML (HyperText Markup Language) is the standard markup language for creating web pages. 
                
HTML describes the structure of a web page using markup tags. Each tag describes different document content.

Key concepts:
- Elements and tags
- Attributes
- Document structure
- Semantic markup

HTML documents are structured with a DOCTYPE declaration, html element, head section, and body section.''',
                'content_fr': '''HTML (HyperText Markup Language) est le langage de balisage standard pour créer des pages web.
                
HTML décrit la structure d'une page web utilisant des balises de balisage. Chaque balise décrit un contenu de document différent.

Concepts clés:
- Éléments et balises
- Attributs
- Structure du document
- Balisage sémantique

Les documents HTML sont structurés avec une déclaration DOCTYPE, un élément html, une section head et une section body.''',
                'order': 1,
                'is_active': True
            }
        )
        
        # Create questions for HTML intro section
        Question.objects.get_or_create(
            section=html_intro_section,
            question_type='section',
            prompt='What does HTML stand for?',
            defaults={
                'prompt_fr': 'Que signifie HTML?',
                'correct_answer': 'HyperText Markup Language',
                'placeholder_hint': 'HyperText _____ Language',
                'order': 1,
                'is_active': True
            }
        )
        
        Question.objects.get_or_create(
            section=html_intro_section,
            question_type='section',
            prompt='Which HTML element is used for the largest heading?',
            defaults={
                'prompt_fr': 'Quel élément HTML est utilisé pour le plus grand titre?',
                'correct_answer': 'h1',
                'placeholder_hint': 'h_',
                'order': 2,
                'is_active': True
            }
        )
        
        # Create more sections for completeness
        html_elements_section, created = Section.objects.get_or_create(
            room=html_room,
            title='HTML Elements and Tags',
            defaults={
                'title_fr': 'Éléments et Balises HTML',
                'content': '''HTML elements are the building blocks of HTML pages. An HTML element is defined by a start tag, some content, and an end tag.

Basic HTML elements include:
- Headings: h1, h2, h3, h4, h5, h6
- Paragraphs: p
- Links: a
- Images: img
- Lists: ul, ol, li
- Divisions: div
- Spans: span

Elements can have attributes that provide additional information about the element.''',
                'order': 2,
                'is_active': True
            }
        )
        
        # Create final exam questions for HTML room
        Question.objects.get_or_create(
            room=html_room,
            question_type='final',
            prompt='Create a basic HTML document structure with DOCTYPE, html, head, and body tags. Write the opening tag for the HTML element.',
            defaults={
                'correct_answer': '<html>',
                'placeholder_hint': '<___>',
                'order': 1,
                'is_active': True
            }
        )
        
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@savoirplus.com',
                password='admin123',
                is_paid_user=True
            )
            self.stdout.write(f'Created admin user: {admin_user.username}')
        
        # Create demo student user
        if not User.objects.filter(username='student').exists():
            student_user = User.objects.create_user(
                username='student',
                email='student@example.com',
                password='student123',
                first_name='Demo',
                last_name='Student'
            )
            self.stdout.write(f'Created student user: {student_user.username}')
        
        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))
        self.stdout.write('You can now log in with:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Student: student / student123')