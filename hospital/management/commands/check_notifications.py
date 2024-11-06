from django.core.management.base import BaseCommand
from hospital.services import NotificationService

class Command(BaseCommand):
    help = 'Check and create notifications for various events'

    def handle(self, *args, **kwargs):
        NotificationService.check_upcoming_appointments()
        NotificationService.check_leave_requests()
        NotificationService.check_low_medicine_stock()
        NotificationService.check_shift_changes()
        
        self.stdout.write(self.style.SUCCESS('Successfully checked notifications')) 