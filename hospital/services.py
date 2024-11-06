from django.utils import timezone
from .models import Notification, Appointment, Patient, LeaveRequest
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import timedelta

class NotificationService:
    @staticmethod
    def create_notification(title, message, notification_type, recipient, priority='medium', link=None, icon=None):
        notification = Notification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            recipient=recipient,
            priority=priority,
            link=link,
            icon=icon or 'fa-bell'
        )
        return notification

    @staticmethod
    def check_upcoming_appointments():
        # Check appointments in next 24 hours
        tomorrow = timezone.now() + timedelta(days=1)
        upcoming_appointments = Appointment.objects.filter(
            date=tomorrow.date(),
            notification_sent=False  # Add this field to Appointment model
        )

        for appointment in upcoming_appointments:
            NotificationService.create_notification(
                title="Upcoming Appointment",
                message=f"Appointment with {appointment.patient.name} tomorrow at {appointment.time}",
                notification_type='appointment',
                recipient=appointment.doctor.employee.user,
                priority='medium',
                link=f'/appointments/{appointment.pk}/',
                icon='fa-calendar'
            )
            appointment.notification_sent = True
            appointment.save()

    @staticmethod
    def check_leave_requests():
        pending_requests = LeaveRequest.objects.filter(
            status='pending',
            notification_sent=False  # Add this field to LeaveRequest model
        )

        # Get all admin users
        admin_users = User.objects.filter(is_staff=True)

        for request in pending_requests:
            for admin in admin_users:
                NotificationService.create_notification(
                    title="New Leave Request",
                    message=f"New leave request from {request.employee.name}",
                    notification_type='leave',
                    recipient=admin,
                    priority='medium',
                    link=f'/hr/leave-requests/{request.pk}/',
                    icon='fa-calendar-alt'
                )
            request.notification_sent = True
            request.save()

    @staticmethod
    def check_low_medicine_stock():
        low_stock_threshold = 10  # Define your threshold
        low_stock_meds = Medication.objects.filter(
            stock__lte=low_stock_threshold,
            notification_sent=False  # Add this field to Medication model
        )

        admin_users = User.objects.filter(is_staff=True)

        for med in low_stock_meds:
            for admin in admin_users:
                NotificationService.create_notification(
                    title="Low Medicine Stock",
                    message=f"Low stock alert for {med.name} (Current stock: {med.stock})",
                    notification_type='general',
                    recipient=admin,
                    priority='high',
                    link=f'/medications/{med.pk}/',
                    icon='fa-pills'
                )
            med.notification_sent = True
            med.save()

    @staticmethod
    def check_shift_changes():
        current_time = timezone.now()
        upcoming_shift = None
        shift_icon = None

        # Determine upcoming shift
        if current_time.hour == 7:  # Morning shift starts at 8 AM
            upcoming_shift = 'morning'
            shift_icon = 'fa-sun'
        elif current_time.hour == 15:  # Evening shift starts at 4 PM
            upcoming_shift = 'evening'
            shift_icon = 'fa-cloud-sun'
        elif current_time.hour == 23:  # Night shift starts at 12 AM
            upcoming_shift = 'night'
            shift_icon = 'fa-moon'

        if upcoming_shift:
            nurses = Nurse.objects.filter(shift=upcoming_shift)
            for nurse in nurses:
                NotificationService.create_notification(
                    title="Upcoming Shift",
                    message=f"Your {upcoming_shift} shift starts in 1 hour",
                    notification_type='shift',
                    recipient=nurse.employee.user,
                    priority='high',
                    icon=shift_icon
                ) 