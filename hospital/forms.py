from django import forms
from .models import (
    Patient, Employee, Doctor, Appointment, Ward, Bed, OTBooking, 
    Payroll, PatientBilling, Medication, Prescription, PrescriptionItem, 
    Ambulance, AmbulanceAssignment, Communication, PatientSerial, 
    LabTest, OPDAppointment, IPDAdmission, Insurance, InsuranceClaim,
    Department, LeaveRequest, Attendance, Performance, Training,
    Notice, Report
)
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
    name = forms.CharField(max_length=100, required=True)
    position = forms.CharField(max_length=100, required=False)
    department = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    email = forms.EmailField(required=False)
    photo = forms.ImageField(required=False)
    joining_date = forms.DateField(required=False)

    class Meta:
        model = Doctor
        fields = ['specialization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.employee:
            self.fields['name'].initial = self.instance.employee.name
            self.fields['position'].initial = self.instance.employee.position
            self.fields['department'].initial = self.instance.employee.department
            self.fields['phone_number'].initial = self.instance.employee.phone_number
            self.fields['email'].initial = self.instance.employee.email
            self.fields['joining_date'].initial = self.instance.employee.joining_date

    def save(self, commit=True):
        doctor = super().save(commit=False)
        
        if doctor.employee:
            employee = doctor.employee
        else:
            employee = Employee()
        
        employee.name = self.cleaned_data['name']
        employee.position = self.cleaned_data['position']
        employee.department = self.cleaned_data['department']
        employee.phone_number = self.cleaned_data['phone_number']
        employee.email = self.cleaned_data['email']
        employee.joining_date = self.cleaned_data['joining_date']
        
        if 'photo' in self.cleaned_data and self.cleaned_data['photo']:
            employee.photo = self.cleaned_data['photo']
        
        if commit:
            employee.save()
            doctor.employee = employee
            doctor.save()
        
        return doctor

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
        fields = ['patient', 'doctor', 'appointment_date', 'reason', 'status']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get all doctors with their employee information
        doctors = Doctor.objects.select_related('employee').all()
        
        # Create choices list with proper formatting
        doctor_choices = []
        for doctor in doctors:
            if doctor.employee:
                name = f"Dr. {doctor.employee.name} - {doctor.specialization or 'No Specialization'}"
            else:
                name = f"Doctor - {doctor.specialization or 'No Specialization'}"
            doctor_choices.append((doctor.id, name))
        
        # Set the choices for the doctor field if any exist
        if doctor_choices:
            self.fields['doctor'].choices = doctor_choices
        
        # Set the label_from_instance for patient field
        self.fields['patient'].label_from_instance = lambda obj: obj.name if obj else "No Name"

class IPDAdmissionForm(forms.ModelForm):
    class Meta:
        model = IPDAdmission
        fields = ['patient', 'doctor', 'admission_date', 'reason', 'bed', 'notes']
        widgets = {
            'admission_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'reason': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available beds
        self.fields['bed'].queryset = Bed.objects.filter(is_occupied=False)
        
        # Format doctor choices
        doctors = Doctor.objects.select_related('employee').all()
        doctor_choices = [(d.id, d.get_name()) for d in doctors]
        self.fields['doctor'].choices = doctor_choices
        
        # Make important fields required
        self.fields['patient'].required = True
        self.fields['doctor'].required = True
        self.fields['admission_date'].required = True
        self.fields['reason'].required = True

class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = ['patient', 'policy_number', 'provider_name', 'policy_type',
                 'coverage_amount', 'start_date', 'end_date', 'status',
                 'documents', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class InsuranceClaimForm(forms.ModelForm):
    class Meta:
        model = InsuranceClaim
        fields = ['insurance', 'patient_billing', 'claimed_amount',
                 'documents', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the insurance instance either from initial data or from the form instance
        insurance = None
        if self.instance.pk:
            insurance = self.instance.insurance
        elif 'insurance' in self.initial:
            insurance = self.initial['insurance']
        
        # Filter patient_billing based on the insurance's patient
        if insurance:
            self.fields['patient_billing'].queryset = PatientBilling.objects.filter(
                patient=insurance.patient
            )
        else:
            self.fields['patient_billing'].queryset = PatientBilling.objects.none()

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date cannot be earlier than start date.")
        return cleaned_data

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'priority', 'expiry_date', 'attachment']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'title', 
            'report_type', 
            'patient', 
            'doctor', 
            'department',
            'diagnosis', 
            'treatment_plan', 
            'prescriptions',
            'file',
            'notes'
        ]
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 4}),
            'treatment_plan': forms.Textarea(attrs={'rows': 4}),
            'prescriptions': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ReportFilterForm(forms.Form):
    report_type = forms.ChoiceField(
        choices=[('', 'All')] + list(Report.REPORT_TYPES), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    date_to = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search reports...'
        })
    )
