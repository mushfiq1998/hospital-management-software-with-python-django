from django import forms
from .models import Patient, Employee, Doctor, Appointment, Ward, Bed, OTBooking, Payroll, PatientBilling, Medication, Prescription, PrescriptionItem, Ambulance, AmbulanceAssignment, Communication, PatientSerial, LabTest, OPDAppointment, IPDAdmission
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'date_of_birth', 'gender', 
                  'phone_number', 'email', 'address', 'photo', 'patient_type']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'position', 'department', 'phone_number', 'email', 'photo']

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'specialization', 'phone_number', 'photo', 'joining_date']
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

class WardForm(forms.ModelForm):
    class Meta:
        model = Ward
        fields = ['name', 'capacity']

class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ['number', 'ward', 'is_occupied']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'ward': forms.Select(attrs={'class': 'form-control'}),
            'is_occupied': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class OTBookingForm(forms.ModelForm):
    class Meta:
        model = OTBooking
        fields = ['patient', 'doctor', 'scheduled_time', 'procedure', 'status', 'notes']
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['employee', 'salary', 'bonus', 'deductions', 'pay_date']
        widgets = {
            'pay_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PatientBillingForm(forms.ModelForm):
    class Meta:
        model = PatientBilling
        fields = ['patient', 'billing_date', 'admission_date', 'release_date', 
                  'daily_rate', 'payment_status', 'description']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'billing_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'admission_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'release_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'daily_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        admission_date = cleaned_data.get('admission_date')
        release_date = cleaned_data.get('release_date')
        daily_rate = cleaned_data.get('daily_rate')

        if admission_date and release_date and release_date < admission_date:
            raise forms.ValidationError("Release date cannot be earlier than admission date.")

        if admission_date and release_date and daily_rate:
            days = (release_date - admission_date).days
            total_amount = days * daily_rate
            cleaned_data['total_amount'] = total_amount

        return cleaned_data

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'company', 'action', 'description', 'price', 'stock']

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'doctor', 'diseases']

class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ['medication', 'dosage', 'frequency']

PrescriptionItemFormSet = inlineformset_factory(
    Prescription, PrescriptionItem, form=PrescriptionItemForm,
    extra=1, can_delete=True
)

class AmbulanceForm(forms.ModelForm):
    class Meta:
        model = Ambulance
        fields = ['vehicle_number', 'model', 'capacity', 'status', 'last_maintenance', 'photo']
        widgets = {
            'last_maintenance': forms.DateInput(attrs={'type': 'date'}),
        }

class AmbulanceAssignmentForm(forms.ModelForm):
    class Meta:
        model = AmbulanceAssignment
        fields = ['ambulance', 'patient', 'notes']

class CommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = ['message']

class PatientSerialForm(forms.ModelForm):
    class Meta:
        model = PatientSerial
        fields = ['patient', 'doctor', 'date', 'serial_number', 'status']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'serial_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['patient', 'test_name', 'test_description', 'doctor', 'status', 'results']
        widgets = {
            'test_description': forms.Textarea(attrs={'rows': 3}),
            'results': forms.Textarea(attrs={'rows': 5}),
        }

class OPDAppointmentForm(forms.ModelForm):
    class Meta:
        model = OPDAppointment
        fields = ['patient', 'doctor', 'appointment_date', 'reason']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class IPDAdmissionForm(forms.ModelForm):
    class Meta:
        model = IPDAdmission
        fields = ['patient', 'doctor', 'admission_date', 'reason']
        widgets = {
            'admission_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
