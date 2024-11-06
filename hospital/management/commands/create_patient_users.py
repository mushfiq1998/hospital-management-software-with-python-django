from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from hospital.models import Patient
from hospital.utils import create_notification

class Command(BaseCommand):
    help = 'Create user accounts for patients who don\'t have one'

    def handle(self, *args, **kwargs):
        patients = Patient.objects.filter(user__isnull=True)
        created_count = 0

        for patient in patients:
            username = patient.email or f"patient_{patient.phone_number}"
            if not username:
                username = f"patient_{get_random_string(8)}"
            
            password = get_random_string(12)
            
            try:
                user = User.objects.create_user(
                    username=username,
                    email=patient.email,
                    password=password
                )
                
                patient.user = user
                patient.save()
                
                create_notification(
                    recipient=user,
                    title='Welcome to Hospital Management System',
                    message=f'Your account has been created.\nUsername: {username}\nPassword: {password}\nPlease change your password after first login.',
                    notification_type='general',
                    priority='high',
                    icon='fa-user-plus'
                )
                
                created_count += 1
                self.stdout.write(f'Created user for patient: {patient.name} (Username: {username})')
                
            except Exception as e:
                self.stderr.write(f'Error creating user for patient {patient.name}: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} user accounts')) 