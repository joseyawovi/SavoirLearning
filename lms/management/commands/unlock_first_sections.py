
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lms.models import Room, Section, SectionCompletion
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Unlock first sections in all rooms for all users'

    def handle(self, *args, **options):
        self.stdout.write('Unlocking first sections in all rooms...')
        
        # Get all active rooms
        rooms = Room.objects.filter(is_active=True)
        
        for room in rooms:
            # Get the first section in each room
            first_section = room.sections.filter(is_active=True).order_by('order').first()
            
            if first_section:
                self.stdout.write(f'Processing room: {room.title}')
                self.stdout.write(f'First section: {first_section.title}')
                
                # Get all users enrolled in this room's roadmap
                from lms.models import Enrollment
                enrolled_users = User.objects.filter(
                    enrollments__roadmap=room.roadmap,
                    enrollments__is_active=True
                ).distinct()
                
                for user in enrolled_users:
                    # Check if section completion record exists
                    section_completion, created = SectionCompletion.objects.get_or_create(
                        user=user,
                        section=first_section,
                        defaults={
                            'is_completed': False,
                            'completed_at': None
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'  Created section completion record for {user.username}')
                    else:
                        self.stdout.write(f'  Section completion record already exists for {user.username}')
        
        self.stdout.write(self.style.SUCCESS('Successfully unlocked first sections!'))
