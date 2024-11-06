from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    LabTest, OTBooking, PatientBilling, Appointment, 
    Prescription, IPDAdmission, OPDAppointment, Patient,
    Doctor, Employee
)
from .utils import create_notification
from django.urls import reverse
from django.contrib.auth.models import User

# Appointment Notifications
@receiver(post_save, sender=Appointment)
def notify_appointment_changes(sender, instance, created, **kwargs):
    if created:
        # Notify patient
        if instance.patient.user:
            create_notification(
                recipient=instance.patient.user,
                title='New Appointment Scheduled',
                message=f'Your appointment with {instance.doctor.get_name()} is scheduled for {instance.date} at {instance.time}',
                notification_type='appointment',
                priority='high',
                link=reverse('appointment_detail', args=[instance.pk]),
                icon='fa-calendar-check'
            )
        
        # Notify doctor
        if instance.doctor.employee and instance.doctor.employee.user:
            create_notification(
                recipient=instance.doctor.employee.user,
                title='New Patient Appointment',
                message=f'New appointment with patient {instance.patient.name} on {instance.date} at {instance.time}',
                notification_type='appointment',
                priority='medium',
                link=reverse('appointment_detail', args=[instance.pk]),
                icon='fa-user-clock'
            )

# Prescription Notifications
@receiver(post_save, sender=Prescription)
def notify_prescription_created(sender, instance, created, **kwargs):
    if created:
        # Notify patient
        if instance.patient.user:
            create_notification(
                recipient=instance.patient.user,
                title='New Prescription',
                message=f'Dr. {instance.doctor.get_name()} has prescribed new medications',
                notification_type='prescription',
                priority='high',
                link=reverse('prescription_detail', args=[instance.pk]),
                icon='fa-prescription'
            )

# Lab Test Notifications
@receiver(post_save, sender=LabTest)
def notify_lab_test_status(sender, instance, created, **kwargs):
    if created:
        # Notify patient
        if instance.patient.user:
            create_notification(
                recipient=instance.patient.user,
                title='New Lab Test Ordered',
                message=f'A new lab test ({instance.test_name}) has been ordered',
                notification_type='lab',
                priority='medium',
                link=reverse('lab_test_detail', args=[instance.pk]),
                icon='fa-flask'
            )
    
    elif instance.status == 'completed':
        # Notify patient
        if instance.patient.user:
            create_notification(
                recipient=instance.patient.user,
                title='Lab Test Results Ready',
                message=f'Your {instance.test_name} results are now available',
                notification_type='lab',
                priority='high',
                link=reverse('lab_test_detail', args=[instance.pk]),
                icon='fa-flask'
            )
        
        # Notify doctor
        if instance.doctor and instance.doctor.employee and instance.doctor.employee.user:
            create_notification(
                recipient=instance.doctor.employee.user,
                title='Lab Test Results Ready',
                message=f'Results for patient {instance.patient.name} - {instance.test_name} are available',
                notification_type='lab',
                priority='medium',
                link=reverse('lab_test_detail', args=[instance.pk]),
                icon='fa-flask'
            )

# IPD Admission Notifications
@receiver(post_save, sender=IPDAdmission)
def notify_admission_status(sender, instance, created, **kwargs):
    if created:
        # Notify patient
        if instance.patient.user:
            create_notification(
                recipient=instance.patient.user,
                title='Hospital Admission',
                message=f'You have been admitted to {instance.bed.ward.name if instance.bed else "hospital"}',
                notification_type='admission',
                priority='high',
                link=reverse('ipd_admission_detail', args=[instance.pk]),
                icon='fa-procedures'
            )
        
        # Notify assigned doctor
        if instance.doctor.employee and instance.doctor.employee.user:
            create_notification(
                recipient=instance.doctor.employee.user,
                title='New Patient Admission',
                message=f'Patient {instance.patient.name} has been admitted under your care',
                notification_type='admission',
                priority='high',
                link=reverse('ipd_admission_detail', args=[instance.pk]),
                icon='fa-user-md'
            )

# OPD Appointment Notifications
@receiver(post_save, sender=OPDAppointment)
def notify_opd_appointment(sender, instance, created, **kwargs):
    if created:
        # Notify patient
        if instance.patient.user:
            create_notification(
                recipient=instance.patient.user,
                title='OPD Appointment Scheduled',
                message=f'Your OPD appointment is scheduled with {instance.doctor.get_name()} on {instance.appointment_date}',
                notification_type='appointment',
                priority='medium',
                link=reverse('opd_appointment_detail', args=[instance.pk]),
                icon='fa-calendar-check'
            )
        
        # Notify doctor
        if instance.doctor.employee and instance.doctor.employee.user:
            create_notification(
                recipient=instance.doctor.employee.user,
                title='New OPD Appointment',
                message=f'New OPD appointment with {instance.patient.name} on {instance.appointment_date}',
                notification_type='appointment',
                priority='medium',
                link=reverse('opd_appointment_detail', args=[instance.pk]),
                icon='fa-calendar-plus'
            )

# Patient Billing Notifications
@receiver(post_save, sender=PatientBilling)
def notify_billing_status(sender, instance, created, **kwargs):
    if created:
        # Notify patient
        if instance.patient.user:
            create_notification(
                recipient=instance.patient.user,
                title='New Billing Statement',
                message=f'A new billing statement of {instance.total_amount} has been generated',
                notification_type='billing',
                priority='high',
                link=reverse('patient_billing_detail', args=[instance.pk]),
                icon='fa-file-invoice-dollar'
            )
    
    elif instance.payment_status == 'unpaid' and instance.is_overdue():
        # Notify patient about overdue payment
        if instance.patient.user:
            create_notification(
                recipient=instance.patient.user,
                title='Payment Overdue',
                message=f'Your payment of {instance.total_amount} is overdue',
                notification_type='billing',
                priority='urgent',
                link=reverse('patient_billing_detail', args=[instance.pk]),
                icon='fa-exclamation-circle'
            )

# OT Booking Notifications
@receiver(post_save, sender=OTBooking)
def notify_ot_booking_status(sender, instance, created, **kwargs):
    if created:
        # Notify patient
        if instance.patient.user:
            create_notification(
                recipient=instance.patient.user,
                title='Operation Scheduled',
                message=f'Your operation is scheduled for {instance.scheduled_time}',
                notification_type='appointment',
                priority='high',
                link=reverse('ot_booking_detail', args=[instance.pk]),
                icon='fa-hospital'
            )
        
        # Notify doctor
        if instance.doctor.employee and instance.doctor.employee.user:
            create_notification(
                recipient=instance.doctor.employee.user,
                title='Operation Scheduled',
                message=f'Operation scheduled with patient {instance.patient.name} at {instance.scheduled_time}',
                notification_type='appointment',
                priority='high',
                link=reverse('ot_booking_detail', args=[instance.pk]),
                icon='fa-hospital-user'
            ) 