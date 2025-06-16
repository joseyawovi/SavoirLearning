
"""
Management command to set up admin user and create mock data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from lms.models import Roadmap, Room, Section, Question
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up admin user and create mock data for LMS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-admin',
            action='store_true',
            help='Skip admin user creation',
        )

    def handle(self, *args, **options):
        # Create admin user if not exists
        if not options['skip_admin']:
            admin_username = 'admin'
            admin_email = 'admin@savoirplus.com'
            admin_password = 'admin123'
            
            if not User.objects.filter(username=admin_username).exists():
                admin_user = User.objects.create_superuser(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                    is_paid_user=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Admin user created: {admin_username} / {admin_password}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Admin user already exists')
                )

        # Create mock data
        self.create_mock_data()
        self.stdout.write(self.style.SUCCESS('Mock data created successfully!'))

    def create_mock_data(self):
        # Create Web Development Roadmap
        web_roadmap, created = Roadmap.objects.get_or_create(
            title="Web Development Fundamentals",
            defaults={
                'title_fr': "Fondamentaux du Développement Web",
                'description': "Complete roadmap for learning web development from basics to advanced concepts.",
                'description_fr': "Feuille de route complète pour apprendre le développement web des bases aux concepts avancés.",
                'is_active': True
            }
        )

        # Create Cybersecurity Roadmap
        cyber_roadmap, created = Roadmap.objects.get_or_create(
            title="Cybersecurity Essentials",
            defaults={
                'title_fr': "Essentiels de la Cybersécurité",
                'description': "Learn cybersecurity fundamentals and ethical hacking techniques.",
                'description_fr': "Apprenez les fondamentaux de la cybersécurité et les techniques de piratage éthique.",
                'is_active': True
            }
        )

        # Create rooms for Web Development
        html_room = self.create_room(
            web_roadmap, "HTML Fundamentals", "Fondamentaux HTML",
            "Learn the building blocks of web pages with HTML.",
            "Apprenez les blocs de construction des pages web avec HTML.",
            order=1
        )

        css_room = self.create_room(
            web_roadmap, "CSS Styling", "Stylisation CSS",
            "Master CSS for beautiful and responsive designs.",
            "Maîtrisez CSS pour des designs beaux et réactifs.",
            order=2, prerequisite=html_room
        )

        js_room = self.create_room(
            web_roadmap, "JavaScript Programming", "Programmation JavaScript",
            "Add interactivity to your websites with JavaScript.",
            "Ajoutez de l'interactivité à vos sites web avec JavaScript.",
            order=3, prerequisite=css_room
        )

        # Create rooms for Cybersecurity
        network_room = self.create_room(
            cyber_roadmap, "Network Security", "Sécurité Réseau",
            "Understand network protocols and security fundamentals.",
            "Comprenez les protocoles réseau et les fondamentaux de sécurité.",
            order=1
        )

        ethical_room = self.create_room(
            cyber_roadmap, "Ethical Hacking", "Piratage Éthique",
            "Learn penetration testing and vulnerability assessment.",
            "Apprenez les tests de pénétration et l'évaluation des vulnérabilités.",
            order=2, prerequisite=network_room
        )

        # Create sections and questions for HTML room
        self.create_html_content(html_room)
        
        # Create sections and questions for Network Security room
        self.create_network_security_content(network_room)

    def create_room(self, roadmap, title, title_fr, description, description_fr, order, prerequisite=None):
        room, created = Room.objects.get_or_create(
            title=title,
            roadmap=roadmap,
            defaults={
                'title_fr': title_fr,
                'description': description,
                'description_fr': description_fr,
                'prerequisite_room': prerequisite,
                'order': order,
                'is_active': True
            }
        )
        return room

    def create_html_content(self, room):
        # Section 1: HTML Basics
        section1 = Section.objects.create(
            room=room,
            title="HTML Structure",
            title_fr="Structure HTML",
            content="""
            <h3>Understanding HTML Structure</h3>
            <p>HTML (HyperText Markup Language) is the standard markup language for creating web pages. It describes the structure of a web page using a series of elements.</p>
            
            <h4>Basic HTML Document Structure:</h4>
            <pre><code>
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;Page Title&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;This is a Heading&lt;/h1&gt;
    &lt;p&gt;This is a paragraph.&lt;/p&gt;
&lt;/body&gt;
&lt;/html&gt;
            </code></pre>
            
            <h4>Key HTML Elements:</h4>
            <ul>
                <li><strong>&lt;DOCTYPE html&gt;</strong> - Declares the document type</li>
                <li><strong>&lt;html&gt;</strong> - Root element of an HTML page</li>
                <li><strong>&lt;head&gt;</strong> - Contains meta information about the page</li>
                <li><strong>&lt;title&gt;</strong> - Specifies a title for the page</li>
                <li><strong>&lt;body&gt;</strong> - Contains the visible page content</li>
            </ul>
            """,
            content_fr="Contenu en français pour la structure HTML...",
            video_url="https://www.youtube.com/watch?v=UB1O30fR-EE",
            order=1,
            is_active=True
        )

        # Questions for Section 1
        Question.objects.create(
            section=section1,
            question_type='section',
            prompt="What does DOCTYPE html declare in an HTML document?",
            prompt_fr="Que déclare DOCTYPE html dans un document HTML ?",
            correct_answer="document type",
            placeholder_hint="_____ ____",
            order=1,
            is_active=True
        )

        Question.objects.create(
            section=section1,
            question_type='section',
            prompt="Which HTML element contains the visible page content?",
            prompt_fr="Quel élément HTML contient le contenu visible de la page ?",
            correct_answer="body",
            placeholder_hint="____",
            order=2,
            is_active=True
        )

        # Section 2: HTML Tags
        section2 = Section.objects.create(
            room=room,
            title="Common HTML Tags",
            title_fr="Balises HTML Communes",
            content="""
            <h3>Essential HTML Tags</h3>
            <p>Learn about the most commonly used HTML tags for structuring content.</p>
            
            <h4>Heading Tags:</h4>
            <pre><code>
&lt;h1&gt;Main Heading&lt;/h1&gt;
&lt;h2&gt;Subheading&lt;/h2&gt;
&lt;h3&gt;Sub-subheading&lt;/h3&gt;
            </code></pre>
            
            <h4>Text Formatting:</h4>
            <ul>
                <li><strong>&lt;p&gt;</strong> - Paragraph</li>
                <li><strong>&lt;strong&gt;</strong> - Important text (bold)</li>
                <li><strong>&lt;em&gt;</strong> - Emphasized text (italic)</li>
                <li><strong>&lt;br&gt;</strong> - Line break</li>
            </ul>
            
            <h4>Lists:</h4>
            <pre><code>
&lt;ul&gt;  &lt;!-- Unordered list --&gt;
    &lt;li&gt;Item 1&lt;/li&gt;
    &lt;li&gt;Item 2&lt;/li&gt;
&lt;/ul&gt;

&lt;ol&gt;  &lt;!-- Ordered list --&gt;
    &lt;li&gt;First item&lt;/li&gt;
    &lt;li&gt;Second item&lt;/li&gt;
&lt;/ol&gt;
            </code></pre>
            """,
            content_fr="Contenu en français pour les balises HTML...",
            order=2,
            is_active=True
        )

        # Questions for Section 2
        Question.objects.create(
            section=section2,
            question_type='section',
            prompt="Which tag is used for creating unordered lists?",
            prompt_fr="Quelle balise est utilisée pour créer des listes non ordonnées ?",
            correct_answer="ul",
            placeholder_hint="__",
            order=1,
            is_active=True
        )

        # Final exam questions for HTML room
        Question.objects.create(
            room=room,
            question_type='final',
            prompt="What is the correct HTML element for the largest heading?",
            prompt_fr="Quel est l'élément HTML correct pour le plus grand titre ?",
            correct_answer="h1",
            placeholder_hint="__",
            order=1,
            is_active=True
        )

        Question.objects.create(
            room=room,
            question_type='final',
            prompt="Which HTML element defines the document type?",
            prompt_fr="Quel élément HTML définit le type de document ?",
            correct_answer="DOCTYPE",
            placeholder_hint="________",
            order=2,
            is_active=True
        )

    def create_network_security_content(self, room):
        # Section 1: Network Fundamentals
        section1 = Section.objects.create(
            room=room,
            title="Network Protocols",
            title_fr="Protocoles Réseau",
            content="""
            <h3>Understanding Network Protocols</h3>
            <p>Network protocols are sets of rules that govern how data is transmitted across networks.</p>
            
            <h4>TCP/IP Stack:</h4>
            <ul>
                <li><strong>Application Layer</strong> - HTTP, HTTPS, FTP, SMTP</li>
                <li><strong>Transport Layer</strong> - TCP, UDP</li>
                <li><strong>Internet Layer</strong> - IP, ICMP</li>
                <li><strong>Network Access Layer</strong> - Ethernet, WiFi</li>
            </ul>
            
            <h4>Common Ports:</h4>
            <ul>
                <li>HTTP: Port 80</li>
                <li>HTTPS: Port 443</li>
                <li>SSH: Port 22</li>
                <li>FTP: Port 21</li>
                <li>DNS: Port 53</li>
            </ul>
            
            <h4>Network Security Fundamentals:</h4>
            <p>Understanding these protocols is crucial for identifying potential security vulnerabilities and implementing proper security measures.</p>
            """,
            content_fr="Contenu en français pour les protocoles réseau...",
            video_url="https://www.youtube.com/watch?v=4_zSIXb7tLQ",
            order=1,
            is_active=True
        )

        # Questions for Network Security
        Question.objects.create(
            section=section1,
            question_type='section',
            prompt="What port does HTTPS typically use?",
            prompt_fr="Quel port HTTPS utilise-t-il généralement ?",
            correct_answer="443",
            placeholder_hint="___",
            order=1,
            is_active=True
        )

        Question.objects.create(
            section=section1,
            question_type='section',
            prompt="Which protocol is used for secure shell connections?",
            prompt_fr="Quel protocole est utilisé pour les connexions shell sécurisées ?",
            correct_answer="SSH",
            placeholder_hint="___",
            order=2,
            is_active=True
        )

        # Final exam questions
        Question.objects.create(
            room=room,
            question_type='final',
            prompt="What does TCP stand for?",
            prompt_fr="Que signifie TCP ?",
            correct_answer="Transmission Control Protocol",
            placeholder_hint="____________ _______ ________",
            order=1,
            is_active=True
        )
