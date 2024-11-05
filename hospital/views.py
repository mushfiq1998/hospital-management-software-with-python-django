from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from .models import (
    Patient, Employee, Doctor, Appointment, Ward, Bed,
    OTBooking, Payroll, PatientBilling, Medication, Prescription,
    Ambulance, AmbulanceAssignment, Communication, LabTest, OPDAppointment,
    IPDAdmission, Insurance, InsuranceClaim, Department, LeaveRequest,
    Notice, Report
)
from .forms import (
    PatientForm, EmployeeForm, DoctorForm, AppointmentForm, 
    WardForm, BedForm, OTBookingForm, PatientBillingForm, MedicationForm,
    PrescriptionForm, AmbulanceForm, AmbulanceAssignmentForm,
    CommunicationForm, LabTestForm, OPDAppointmentForm, IPDAdmissionForm,
    InsuranceForm, InsuranceClaimForm, LeaveRequestForm,
    NoticeForm, ReportForm, ReportFilterForm  # Add these forms
)
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DeleteView, ListView, CreateView, \
    UpdateView, DetailView
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from .forms import UserProfileForm
from .forms import PayrollForm
from django.db.models import Sum
from .models import Prescription, PrescriptionItem
from .forms import PrescriptionForm, PrescriptionItemFormSet
from .models import PatientSerial
from .forms import PatientSerialForm
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from .models import Appointment
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import LabTest
from .forms import LabTestForm
from django.http import FileResponse
from django.db import models
from django.db.models import Q

# Dashboard View
@login_required
def dashboard(request):
    employees_count = Employee.objects.count()
    patients_count = Patient.objects.count()
    indoor_patients_count = Patient.objects.filter(patient_type='indoor').count()
    outdoor_patients_count = Patient.objects.filter(patient_type='outdoor').count()
    doctors_count = Doctor.objects.count()
    appointments_count = Appointment.objects.count()
    wards_count = Ward.objects.count()
    beds_count = Bed.objects.count()
    patients = Patient.objects.all()
    upcoming_ot_bookings = OTBooking.objects.filter(status='scheduled', scheduled_time__gt=timezone.now()).count()
    ongoing_ot_bookings = OTBooking.objects.filter(status='in_progress').count()
    payroll_count = Payroll.objects.count()
    
    total_billing = PatientBilling.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    unpaid_billing = PatientBilling.objects.filter(payment_status='unpaid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Add this line to get the total number of ambulances
    ambulances_count = Ambulance.objects.count()
    
    # Add this to get today's patient serials count
    today = timezone.now().date()
    patient_serials_count = PatientSerial.objects.filter(date=today).count()
    
    # Add OPD statistics
    today = timezone.now().date()
    opd_appointments_count = OPDAppointment.objects.count()
    today_opd_appointments_count = OPDAppointment.objects.filter(
        appointment_date__date=today
    ).count()

    # Add IPD statistics
    ipd_admissions_count = IPDAdmission.objects.filter(status='admitted').count()
    
    # Add these lines for insurance statistics
    active_insurance_count = Insurance.objects.filter(status='active').count()
    pending_claims_count = InsuranceClaim.objects.filter(status='pending').count()
    
    # Add HR statistics
    departments_count = Department.objects.count()
    pending_leave_requests = LeaveRequest.objects.filter(status='pending').count()
    
    # Add these to your dashboard view
    notices = Notice.objects.filter(is_active=True)
    recent_notices = notices.order_by('-created_at')[:5]
    
    # Get reports statistics
    reports_count = Report.objects.filter(is_archived=False).count()
    recent_reports_count = Report.objects.filter(
        is_archived=False,
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    
    context = {
        'employees_count': employees_count,
        'patients_count': patients_count,
        'indoor_patients_count': indoor_patients_count,
        'outdoor_patients_count': outdoor_patients_count,
        'doctors_count': doctors_count,
        'appointments_count': appointments_count,
        'wards_count': wards_count,
        'beds_count': beds_count,
        'patients': patients,
        'upcoming_ot_bookings': upcoming_ot_bookings,
        'ongoing_ot_bookings': ongoing_ot_bookings,
        'payroll_count': payroll_count,
        'total_billing': total_billing,
        'unpaid_billing': unpaid_billing,
        'ambulances_count': ambulances_count,  # Add this line
        'patient_serials_count': patient_serials_count,
        'opd_appointments_count': opd_appointments_count,
        'today_opd_appointments_count': today_opd_appointments_count,
        'ipd_admissions_count': ipd_admissions_count,
        'active_insurance_count': active_insurance_count,
        'pending_claims_count': pending_claims_count,
        'departments_count': departments_count,
        'pending_leave_requests': pending_leave_requests,
        'notices': notices,
        'recent_notices': recent_notices,
        'reports_count': reports_count,
        'recent_reports_count': recent_reports_count,
    }
    return render(request, 'hospital/dashboard.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'hospital/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {username}! You have been logged in.")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'hospital/login.html', {'form': form})

def user_logout(request):
    username = request.user.username
    logout(request)
    messages.success(request, f"Goodbye, {username}! You have been logged out.")
    return redirect('login')

# .......................................................................
# Patient Views ..........................................................
@login_required
def patient_list(request):
    patient_type = request.GET.get('type', 'all')
    if patient_type == 'indoor':
        patients = Patient.objects.filter(patient_type='indoor')
    elif patient_type == 'outdoor':
        patients = Patient.objects.filter(patient_type='outdoor')
    else:
        patients = Patient.objects.all()
    context = {'patients': patients, 'current_type': patient_type}
    return render(request, 'hospital/patient_list.html', context)

@login_required
def patient_add(request):
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'hospital/patient_form.html', {'form': form})

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    context = {'patient': patient}
    return render(request, 'hospital/patient_detail.html', context)

@login_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'hospital/patient_form.html', {'form': form})

def delete_object(request, model, pk, redirect_url):
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect(redirect_url)
    context = {
        'object': obj,
        'cancel_url': reverse(redirect_url)
    }
    return render(request, 'hospital/confirm_delete.html', context)

@login_required
def patient_delete(request, pk):
    return delete_object(request, Patient, pk, 'patient_list')


@login_required
def admit_patient(request, pk):
    if pk == 0:
        # This is called from the dashboard
        patient_id = request.GET.get('patient_id')
        if patient_id:
            return redirect('admit_patient', pk=patient_id)
        else:
            messages.error(request, "Please select a patient to admit.")
            return redirect('dashboard')
    
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        bed_id = request.POST.get('bed_id')
        if bed_id:
            bed = get_object_or_404(Bed, pk=bed_id)
            if not bed.is_occupied:
                # Check if the patient is already assigned to a bed
                if patient.bed:
                    # If so, free up the old bed
                    old_bed = patient.bed
                    old_bed.is_occupied = False
                    old_bed.save()
                
                patient.is_admitted = True
                patient.admission_date = timezone.now()
                patient.bed = bed
                patient.save()
                
                bed.is_occupied = True
                bed.save()
                
                messages.success(request, 
                    f"Patient {patient.name} has been admitted and assigned to bed {bed.number}.")
                return redirect('patient_detail', pk=patient.pk)
            else:
                messages.error(request, "The selected bed is already occupied.")
        else:
            messages.error(request, "Please select a bed for admission.")
    
    available_beds = Bed.objects.filter(is_occupied=False)
    context = {'patient': patient, 'available_beds': available_beds}
    return render(request, 'hospital/admit_patient.html', context)


def patient_pdf(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    template_path = 'hospital/patient_pdf.html'
    context = {'patient': patient}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="patient_{patient_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


# .......................................................................
# Employee Views 
@login_required
def employee_list(request):
    employees = Employee.objects.all()
    context = {'employees': employees}
    return render(request, 'hospital/employee_list.html', context)

@login_required
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'hospital/employee_form.html', {'form': form})

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    context = {'employee': employee}
    return render(request, 'hospital/employee_detail.html', context)

@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'hospital/employee_form.html', {'form': form})

@login_required
def employee_delete(request, pk):
    return delete_object(request, Employee, pk, 'employee_list')

@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'hospital/employee_form.html', {'form': form})
    

def employee_pdf(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    template_path = 'hospital/employee_pdf.html'
    context = {'employee': employee}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="employee_{employee_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# .......................................................................
# Doctor Views ..........................................................
@login_required
def doctor_list(request):
    doctors = Doctor.objects.all()
    context = {'doctors': doctors}
    return render(request, 'hospital/doctor_list.html', context)

@login_required
def doctor_add(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'hospital/doctor_form.html', {'form': form})

@login_required
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    context = {'doctor': doctor}
    return render(request, 'hospital/doctor_detail.html', context)

@login_required
def doctor_edit(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('doctor_list')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'hospital/doctor_form.html', {'form': form})

@login_required
def doctor_delete(request, pk):
    return delete_object(request, Doctor, pk, 'doctor_list')

@login_required
def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'hospital/doctor_form.html', {'form': form})


def doctor_pdf(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    template_path = 'hospital/doctor_pdf.html'
    context = {'doctor': doctor}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="doctor_{doctor_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# ......................................................................
# Appointment Views ....................................................
@login_required
def appointment_list(request):
    appointments = Appointment.objects.all()
    context = {'appointments': appointments}
    return render(request, 'hospital/appointment_list.html', context)

@login_required
def appointment_add(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'hospital/appointment_form.html', {'form': form})

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    context = {'appointment': appointment}
    return render(request, 'hospital/appointment_detail.html', context)

@login_required
def appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'hospital/appointment_form.html', {'form': form})

@login_required
def appointment_delete(request, pk):
    return delete_object(request, Appointment, pk, 'appointment_list')

def appointment_pdf(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    template_path = 'hospital/appointment_pdf.html'
    context = {'appointment': appointment}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="appointment_{appointment_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# ......................................................................
# Ward Views ..........................................................
@login_required
def ward_list(request):
    wards = Ward.objects.all()
    return render(request, 'hospital/ward_list.html', {'wards': wards})

@login_required
def ward_detail(request, pk):
    ward = get_object_or_404(Ward, pk=pk)
    beds = ward.beds.all()
    return render(request, 'hospital/ward_detail.html', {'ward': ward, 'beds': beds})

@login_required
def ward_create(request):
    if request.method == 'POST':
        form = WardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ward_list')
    else:
        form = WardForm()
    return render(request, 'hospital/ward_form.html', {'form': form})

@login_required
def ward_update(request, pk):
    ward = get_object_or_404(Ward, pk=pk)
    if request.method == 'POST':
        form = WardForm(request.POST, instance=ward)
        if form.is_valid():
            form.save()
            return redirect('ward_detail', pk=ward.pk)
    else:
        form = WardForm(instance=ward)
    return render(request, 'hospital/ward_form.html', {'form': form})
    

def ward_pdf(request, ward_id):
    ward = get_object_or_404(Ward, id=ward_id)
    beds = ward.beds.all()
    template_path = 'hospital/ward_pdf.html'
    context = {'ward': ward, 'beds': beds}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="ward_{ward_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


# Bed Views
@login_required
def bed_list(request):
    beds = Bed.objects.all()
    return render(request, 'hospital/bed_list.html', {'beds': beds})

@login_required
def bed_detail(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    return render(request, 'hospital/bed_detail.html', {'bed': bed})

@login_required
def bed_create(request):
    if request.method == 'POST':
        form = BedForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bed_list')
    else:
        form = BedForm()
    return render(request, 'hospital/bed_form.html', {'form': form})

@login_required
def bed_update(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    if request.method == 'POST':
        form = BedForm(request.POST, instance=bed)
        if form.is_valid():
            form.save()
            return redirect('bed_detail', pk=bed.pk)
    else:
        form = BedForm(instance=bed)
    return render(request, 'hospital/bed_form.html', {'form': form})

@login_required
def assign_bed(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        bed_id = request.POST.get('bed_id')
        bed = get_object_or_404(Bed, pk=bed_id)
        if not bed.is_occupied:
            bed.is_occupied = True
            bed.patient = patient
            bed.save()
            patient.bed = bed
            patient.save()
            messages.success(request, f"Bed {bed.number} assigned to {patient.name}")
        else:
            messages.error(request, "This bed is already occupied")
        return redirect('patient_detail', pk=patient_id)
    
    available_beds = Bed.objects.filter(is_occupied=False)
    context = {'patient': patient, 'available_beds': available_beds}
    return render(request, 'hospital/assign_bed.html', context)

class WardDeleteView(DeleteView):
    model = Ward
    success_url = reverse_lazy('ward_list')
    template_name = 'hospital/ward_confirm_delete.html'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

ward_delete = WardDeleteView.as_view()

@login_required
def bed_delete(request, pk):
    return delete_object(request, Bed, pk, 'bed_list')


def bed_pdf(request, bed_id):
    bed = get_object_or_404(Bed, id=bed_id)
    template_path = 'hospital/bed_pdf.html'
    context = {'bed': bed}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="bed_{bed_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
def ot_booking_list(request):
    bookings = OTBooking.objects.all().order_by('scheduled_time')
    return render(request, 'hospital/ot_booking_list.html', {'bookings': bookings})

@login_required
def ot_booking_create(request):
    if request.method == 'POST':
        form = OTBookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'OT Booking created successfully.')
            return redirect('ot_booking_list')
    else:
        form = OTBookingForm()
    return render(request, 'hospital/ot_booking_form.html', {'form': form})

@login_required
def ot_booking_update(request, pk):
    booking = get_object_or_404(OTBooking, pk=pk)
    if request.method == 'POST':
        form = OTBookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'OT Booking updated successfully.')
            return redirect('ot_booking_list')
    else:
        form = OTBookingForm(instance=booking)
    return render(request, 'hospital/ot_booking_form.html', {'form': form})

@login_required
def ot_booking_delete(request, pk):
    booking = get_object_or_404(OTBooking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'OT Booking deleted successfully.')
        return redirect('ot_booking_list')
    return render(request, 'hospital/ot_booking_confirm_delete.html', {'booking': booking})

@login_required
def ot_booking_detail(request, pk):
    booking = get_object_or_404(OTBooking, pk=pk)
    return render(request, 'hospital/ot_booking_detail.html', {'booking': booking})


def ot_booking_pdf(request, booking_id):
    booking = get_object_or_404(OTBooking, id=booking_id)
    template_path = 'hospital/ot_booking_pdf.html'
    context = {'booking': booking}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="ot_booking_{booking_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'hospital/change_password.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'hospital/profile.html', {'form': form})

@login_required
def account_management(request):
    return render(request, 'hospital/account_management.html')

@login_required
def view_profile(request):
    return render(request, 'hospital/view_profile.html', {'user': request.user})

@login_required
def payroll_list(request):
    payrolls = Payroll.objects.all().order_by('-pay_date')
    return render(request, 'hospital/payroll_list.html', {'payrolls': payrolls})

@login_required
def payroll_add(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll record added successfully.')
            return redirect('payroll_list')
    else:
        form = PayrollForm()
    return render(request, 'hospital/payroll_form.html', {'form': form})

@login_required
def payroll_edit(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    if request.method == 'POST':
        form = PayrollForm(request.POST, instance=payroll)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll record updated successfully.')
            return redirect('payroll_list')
    else:
        form = PayrollForm(instance=payroll)
    return render(request, 'hospital/payroll_form.html', {'form': form})

@login_required
def payroll_view(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    return render(request, 'hospital/payroll_detail.html', {'payroll': payroll})

@login_required
def payroll_delete(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    if request.method == 'POST':
        payroll.delete()
        messages.success(request, 'Payroll record deleted successfully.')
        return redirect('payroll_list')
    return render(request, 'hospital/payroll_confirm_delete.html', {'payroll': payroll})


def payroll_pdf(request, payroll_id):
    payroll = get_object_or_404(Payroll, id=payroll_id)
    template_path = 'hospital/payroll_pdf.html'
    context = {'payroll': payroll}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="payroll_{payroll_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


# Add these new views for patient billing
@login_required
def patient_billing_list(request):
    billings = PatientBilling.objects.all().order_by('-billing_date')
    return render(request, 'hospital/patient_billing_list.html', {'billings': billings})

@login_required
def patient_billing_add(request):
    if request.method == 'POST':
        form = PatientBillingForm(request.POST)
        if form.is_valid():
            billing = form.save(commit=False)
            billing.total_amount = billing.calculate_total_amount()
            billing.save()
            messages.success(request, 'Patient billing record added successfully.')
            return redirect('patient_billing_list')
    else:
        form = PatientBillingForm()
    return render(request, 'hospital/patient_billing_form.html', {'form': form})

@login_required
def patient_billing_edit(request, pk):
    billing = get_object_or_404(PatientBilling, pk=pk)
    if request.method == 'POST':
        form = PatientBillingForm(request.POST, instance=billing)
        if form.is_valid():
            billing = form.save(commit=False)
            billing.total_amount = billing.calculate_total_amount()
            billing.save()
            messages.success(request, 'Patient billing record updated successfully.')
            return redirect('patient_billing_list')
    else:
        form = PatientBillingForm(instance=billing)
    return render(request, 'hospital/patient_billing_form.html', {'form': form})

@login_required
def patient_billing_view(request, pk):
    billing = get_object_or_404(PatientBilling, pk=pk)
    return render(request, 'hospital/patient_billing_detail.html', {'billing': billing})

@login_required
def patient_billing_delete(request, pk):
    billing = get_object_or_404(PatientBilling, pk=pk)
    if request.method == 'POST':
        billing.delete()
        messages.success(request, 'Patient billing record deleted successfully.')
        return redirect('patient_billing_list')
    return render(request, 'hospital/patient_billing_confirm_delete.html', {'billing': billing})


def patient_billing_pdf(request, patient_billing_id):
    patient_billing = get_object_or_404(PatientBilling, id=patient_billing_id)
    template_path = 'hospital/patient_billing_pdf.html'
    context = {'patient_billing': patient_billing}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="payroll_{patient_billing_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


class MedicationListView(ListView):
    model = Medication
    template_name = 'hospital/medication_list.html'
    context_object_name = 'medications'

class MedicationCreateView(CreateView):
    model = Medication
    form_class = MedicationForm
    template_name = 'hospital/medication_form.html'
    success_url = reverse_lazy('medication_list')

class MedicationUpdateView(UpdateView):
    model = Medication
    form_class = MedicationForm
    template_name = 'hospital/medication_form.html'
    success_url = reverse_lazy('medication_list')

class MedicationDeleteView(DeleteView):
    model = Medication
    template_name = 'hospital/medication_confirm_delete.html'
    success_url = reverse_lazy('medication_list')

class MedicationDetailView(DetailView):
    model = Medication
    template_name = 'hospital/medication_detail.html'
    context_object_name = 'medication'

def medication_pdf(request, medication_id):
    medication = get_object_or_404(Medication, id=medication_id)
    template_path = 'hospital/medication_pdf.html'
    context = {'medication': medication}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="medication_{medication_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

class PrescriptionListView(ListView):
    model = Prescription
    template_name = 'hospital/prescription_list.html'
    context_object_name = 'prescriptions'

class PrescriptionCreateView(CreateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'hospital/prescription_form.html'
    success_url = reverse_lazy('prescription_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = PrescriptionItemFormSet(self.request.POST)
        else:
            data['items'] = PrescriptionItemFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        self.object = form.save()
        if items.is_valid():
            items.instance = self.object
            items.save()
        return super().form_valid(form)

class PrescriptionUpdateView(UpdateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'hospital/prescription_form.html'
    success_url = reverse_lazy('prescription_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = PrescriptionItemFormSet(self.request.POST, instance=self.object)
        else:
            data['items'] = PrescriptionItemFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        self.object = form.save()
        if items.is_valid():
            items.instance = self.object
            items.save()
        return super().form_valid(form)

class PrescriptionDetailView(DetailView):
    model = Prescription
    template_name = 'hospital/prescription_detail.html'
    context_object_name = 'prescription'

class PrescriptionDeleteView(DeleteView):
    model = Prescription
    template_name = 'hospital/prescription_confirm_delete.html'
    success_url = reverse_lazy('prescription_list')

def prescription_pdf(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    template_path = 'hospital/prescription_pdf.html'
    context = {'prescription': prescription}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="prescription_{prescription_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def fill_prescription(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    if not prescription.is_filled:
        for item in prescription.items.all():
            if item.medication.stock > 0:
                item.medication.stock -= 1
                item.medication.save()
            else:
                # Handle the case when there's not enough stock
                pass
        prescription.is_filled = True
        prescription.save()
    return redirect('prescription_list')

class AmbulanceListView(ListView):
    model = Ambulance
    template_name = 'hospital/ambulance_list.html'
    context_object_name = 'ambulances'

class AmbulanceDetailView(DetailView):
    model = Ambulance
    template_name = 'hospital/ambulance_detail.html'
    context_object_name = 'ambulance'

class AmbulanceCreateView(CreateView):
    model = Ambulance
    form_class = AmbulanceForm
    template_name = 'hospital/ambulance_form.html'
    success_url = reverse_lazy('ambulance_list')

class AmbulanceUpdateView(UpdateView):
    model = Ambulance
    form_class = AmbulanceForm
    template_name = 'hospital/ambulance_form.html'
    success_url = reverse_lazy('ambulance_list')

class AmbulanceDeleteView(DeleteView):
    model = Ambulance
    template_name = 'hospital/ambulance_confirm_delete.html'
    success_url = reverse_lazy('ambulance_list')

def ambulance_pdf(request, ambulance_id):
    ambulance = get_object_or_404(Ambulance, id=ambulance_id)
    template_path = 'hospital/ambulance_pdf.html'
    context = {'ambulance': ambulance}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="ambulance_{ambulance_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def assign_ambulance(request):
    ambulance_id = request.GET.get('ambulance_id')
    initial_data = {}
    if ambulance_id:
        ambulance = get_object_or_404(Ambulance, id=ambulance_id)
        initial_data['ambulance'] = ambulance

    if request.method == 'POST':
        form = AmbulanceAssignmentForm(request.POST, initial=initial_data)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.status = 'assigned'
            assignment.save()
            messages.success(request, 'Ambulance assigned successfully.')
            return redirect('assignment_detail', pk=assignment.pk)
    else:
        form = AmbulanceAssignmentForm(initial=initial_data)
    return render(request, 'hospital/assign_ambulance.html', {'form': form})

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(AmbulanceAssignment, pk=pk)
    communications = assignment.communications.all().order_by('-timestamp')
    
    if request.method == 'POST':
        if 'complete_assignment' in request.POST:
            assignment.status = 'completed'
            assignment.completed_at = timezone.now()
            assignment.ambulance.status = 'available'
            assignment.ambulance.save()
            assignment.save()
            messages.success(request, 'Assignment marked as completed.')
            return redirect('assignment_detail', pk=pk)
        else:
            form = CommunicationForm(request.POST)
            if form.is_valid():
                communication = form.save(commit=False)
                communication.assignment = assignment
                communication.sender = request.user
                communication.save()
                return redirect('assignment_detail', pk=pk)
    else:
        form = CommunicationForm()
    
    context = {
        'assignment': assignment,
        'communications': communications,
        'form': form,
    }
    return render(request, 'hospital/assignment_detail.html', context)

@login_required
def patient_serial_list(request):
    today = timezone.now().date()
    serials = PatientSerial.objects.filter(date=today)
    return render(request, 'hospital/patient_serial_list.html', {'serials': serials})

@login_required
def create_patient_serial(request):
    if request.method == 'POST':
        form = PatientSerialForm(request.POST)
        if form.is_valid():
            serial = form.save(commit=False)
            
            # Check if a serial with the same doctor, date, and serial number already exists
            existing_serial = PatientSerial.objects.filter(
                doctor=serial.doctor,
                date=serial.date,
                serial_number=serial.serial_number
            ).exists()
            
            if existing_serial:
                messages.error(request, 'A serial with this number already exists for the selected doctor and date.')
            else:
                serial.save()
                messages.success(request, 'Patient serial created successfully.')
                return redirect('patient_serial_list')
    else:
        form = PatientSerialForm(initial={'date': timezone.now().date()})
    
    context = {
        'form': form,
        'patients': Patient.objects.all(),
        'doctors': Doctor.objects.all(),
        'status_choices': PatientSerial.STATUS_CHOICES,
    }
    return render(request, 'hospital/patient_serial_form.html', context)

@login_required
def update_patient_serial_status(request, pk):
    serial = get_object_or_404(PatientSerial, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(PatientSerial.status_choices):
            serial.status = new_status
            serial.save()
            messages.success(request, f'Serial status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status.')
    return redirect('patient_serial_list')

def patient_serial_detail(request, pk):
    serial = get_object_or_404(PatientSerial, pk=pk)
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    status_choices = PatientSerial.STATUS_CHOICES

    context = {
        'serial': serial,
        'patients': patients,
        'doctors': doctors,
        'status_choices': status_choices,
    }
    return render(request, 'hospital/patient_serial_detail.html', context)

def edit_patient_serial(request, pk):
    serial = get_object_or_404(PatientSerial, pk=pk)
    if request.method == 'POST':
        form = PatientSerialForm(request.POST, instance=serial)
        if form.is_valid():
            form.save()
            return redirect('patient_serial_list')
    else:
        form = PatientSerialForm(instance=serial)
    return render(request, 'hospital/patient_serial_form.html', {'form': form})

def delete_patient_serial(request, pk):
    serial = get_object_or_404(PatientSerial, pk=pk)
    if request.method == 'POST':
        serial.delete()
        return redirect('patient_serial_list')
    return render(request, 'hospital/patient_serial_confirm_delete.html', {'serial': serial})


def patient_serial_pdf(request, serial_id):
    serial = get_object_or_404(PatientSerial, id=serial_id)
    template_path = 'hospital/patient_serial_pdf.html'
    context = {'serial': serial}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="patient_serial_{serial_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

class LabTestListView(LoginRequiredMixin, ListView):
    model = LabTest
    template_name = 'hospital/lab_test_list.html'
    context_object_name = 'lab_tests'
    
    def get_queryset(self):
        return LabTest.objects.all().order_by('-date_ordered')

class LabTestCreateView(LoginRequiredMixin, CreateView):
    model = LabTest
    form_class = LabTestForm
    template_name = 'hospital/lab_test_form.html'
    success_url = reverse_lazy('lab_test_list')

    def form_valid(self, form):
        messages.success(self.request, 'Lab test created successfully.')
        return super().form_valid(form)

class LabTestUpdateView(LoginRequiredMixin, UpdateView):
    model = LabTest
    form_class = LabTestForm
    template_name = 'hospital/lab_test_form.html'
    success_url = reverse_lazy('lab_test_list')

    def form_valid(self, form):
        messages.success(self.request, 'Lab test updated successfully.')
        return super().form_valid(form)

class LabTestDeleteView(LoginRequiredMixin, DeleteView):
    model = LabTest
    template_name = 'hospital/lab_test_confirm_delete.html'
    success_url = reverse_lazy('lab_test_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Lab test deleted successfully.')
        return super().delete(request, *args, **kwargs)

class LabTestDetailView(LoginRequiredMixin, DetailView):
    model = LabTest
    template_name = 'hospital/lab_test_detail.html'
    context_object_name = 'lab_test'

@login_required
def complete_lab_test(request, pk):
    lab_test = get_object_or_404(LabTest, pk=pk)
    if lab_test.status != 'completed':
        lab_test.status = 'completed'
        lab_test.date_completed = timezone.now()
        lab_test.save()
        messages.success(request, 'Lab test marked as completed.')
    return redirect('lab_test_detail', pk=pk)


def lab_test_pdf(request, lab_test_id):
    lab_test = get_object_or_404(LabTest, id=lab_test_id)
    template_path = 'hospital/lab_test_pdf.html'
    context = {'lab_test': lab_test}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="lab_test_{lab_test_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# Add these views for OPD Appointments
@login_required
def opd_appointment_list(request):
    appointments = OPDAppointment.objects.all().order_by('-appointment_date')
    return render(request, 'hospital/opd_appointment_list.html', 
                  {'appointments': appointments})

@login_required
def opd_appointment_detail(request, pk):
    appointment = get_object_or_404(OPDAppointment, pk=pk)
    return render(request, 'hospital/opd_appointment_detail.html', 
                  {'appointment': appointment})

@login_required
def opd_appointment_create(request):
    if request.method == 'POST':
        form = OPDAppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'OPD Appointment created successfully.')
            return redirect('opd_appointment_list')
    else:
        form = OPDAppointmentForm()
    return render(request, 'hospital/opd_appointment_form.html', {'form': form})

@login_required
def opd_appointment_edit(request, pk):
    appointment = get_object_or_404(OPDAppointment, pk=pk)
    if request.method == 'POST':
        form = OPDAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'OPD Appointment updated successfully.')
            return redirect('opd_appointment_list')
    else:
        form = OPDAppointmentForm(instance=appointment)
    return render(request, 'hospital/opd_appointment_form.html', {'form': form})

@login_required
def opd_appointment_delete(request, pk):
    appointment = get_object_or_404(OPDAppointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'OPD Appointment deleted successfully.')
        return redirect('opd_appointment_list')
    return render(request, 'hospital/opd_appointment_confirm_delete.html', 
                  {'appointment': appointment})


def opd_appointment_pdf(request, appointment_id):
    appointment = get_object_or_404(OPDAppointment, id=appointment_id)
    template_path = 'hospital/opd_appointment_pdf.html'
    context = {'appointment': appointment}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="opd_appointment_{appointment_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


# Add these view functions to your views.py
@login_required
def ipd_admission_list(request):
    admissions = IPDAdmission.objects.all().order_by('-admission_date')
    return render(request, 'hospital/ipd_admission_list.html', 
                  {'admissions': admissions})

@login_required
def ipd_admission_create(request):
    if request.method == 'POST':
        form = IPDAdmissionForm(request.POST)
        if form.is_valid():
            admission = form.save(commit=False)
            admission.status = 'admitted'
            
            # Update bed status if bed is assigned
            if admission.bed:
                admission.bed.is_occupied = True
                admission.bed.save()
                
            admission.save()
            messages.success(request, 'IPD Admission created successfully.')
            return redirect('ipd_admission_list')
    else:
        form = IPDAdmissionForm()
    return render(request, 'hospital/ipd_admission_form.html', {'form': form})

@login_required
def ipd_admission_detail(request, pk):
    admission = get_object_or_404(IPDAdmission, pk=pk)
    return render(request, 'hospital/ipd_admission_detail.html', 
                  {'admission': admission})

@login_required
def ipd_admission_edit(request, pk):
    admission = get_object_or_404(IPDAdmission, pk=pk)
    if request.method == 'POST':
        form = IPDAdmissionForm(request.POST, instance=admission)
        if form.is_valid():
            # Handle bed changes
            old_bed = admission.bed
            new_bed = form.cleaned_data.get('bed')
            
            if old_bed != new_bed:
                if old_bed:
                    old_bed.is_occupied = False
                    old_bed.save()
                if new_bed:
                    new_bed.is_occupied = True
                    new_bed.save()
            
            form.save()
            messages.success(request, 'IPD Admission updated successfully.')
            return redirect('ipd_admission_detail', pk=admission.pk)
    else:
        form = IPDAdmissionForm(instance=admission)
    return render(request, 'hospital/ipd_admission_form.html', {'form': form})

@login_required
def ipd_admission_discharge(request, pk):
    admission = get_object_or_404(IPDAdmission, pk=pk)
    if admission.status == 'admitted':
        admission.status = 'discharged'
        admission.discharge_date = timezone.now()
        
        # Free up the bed
        if admission.bed:
            admission.bed.is_occupied = False
            admission.bed.save()
        
        admission.save()
        messages.success(request, f'Patient {admission.patient.name} has been discharged.')
    return redirect('ipd_admission_detail', pk=admission.pk)


def ipd_admission_pdf(request, admission_id):
    admission = get_object_or_404(IPDAdmission, id=admission_id)
    template_path = 'hospital/ipd_admission_pdf.html'
    context = {'admission': admission}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="ipd_admission_{admission_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# Add these to your views.py
@login_required
def insurance_list(request):
    insurances = Insurance.objects.all().order_by('-created_at')
    return render(request, 'hospital/insurance_list.html', 
                  {'insurances': insurances})

@login_required
def insurance_create(request):
    if request.method == 'POST':
        form = InsuranceForm(request.POST, request.FILES)
        if form.is_valid():
            insurance = form.save()
            messages.success(request, 'Insurance policy created successfully.')
            return redirect('insurance_detail', pk=insurance.pk)
    else:
        form = InsuranceForm()
    return render(request, 'hospital/insurance_form.html', {'form': form})

@login_required
def insurance_detail(request, pk):
    insurance = get_object_or_404(Insurance, pk=pk)
    claims = insurance.claims.all().order_by('-created_at')
    return render(request, 'hospital/insurance_detail.html', 
                 {'insurance': insurance, 'claims': claims})

@login_required
def insurance_edit(request, pk):
    insurance = get_object_or_404(Insurance, pk=pk)
    if request.method == 'POST':
        form = InsuranceForm(request.POST, request.FILES, instance=insurance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Insurance policy updated successfully.')
            return redirect('insurance_detail', pk=insurance.pk)
    else:
        form = InsuranceForm(instance=insurance)
    return render(request, 'hospital/insurance_form.html', {'form': form})

@login_required
def insurance_delete(request, pk):
    insurance = get_object_or_404(Insurance, pk=pk)
    if request.method == 'POST':
        insurance.delete()
        messages.success(request, 'Insurance policy deleted successfully.')
        return redirect('insurance_list')
    return render(request, 'hospital/insurance_confirm_delete.html', 
                 {'insurance': insurance})

@login_required
def insurance_claim_list(request):
    claims = InsuranceClaim.objects.all().order_by('-created_at')
    return render(request, 'hospital/insurance_claim_list.html', 
                  {'claims': claims})

@login_required
def insurance_claim_create(request):
    if request.method == 'POST':
        form = InsuranceClaimForm(request.POST, request.FILES)
        if form.is_valid():
            claim = form.save()
            messages.success(request, 'Insurance claim created successfully.')
            return redirect('insurance_claim_detail', pk=claim.pk)
    else:
        insurance_id = request.GET.get('insurance')
        initial = {}
        if insurance_id:
            insurance = get_object_or_404(Insurance, pk=insurance_id)
            initial['insurance'] = insurance
        form = InsuranceClaimForm(initial=initial)
    return render(request, 'hospital/insurance_claim_form.html', {'form': form})

@login_required
def insurance_claim_detail(request, pk):
    claim = get_object_or_404(InsuranceClaim, pk=pk)
    return render(request, 'hospital/insurance_claim_detail.html', 
                  {'claim': claim})

@login_required
def insurance_claim_edit(request, pk):
    claim = get_object_or_404(InsuranceClaim, pk=pk)
    if request.method == 'POST':
        form = InsuranceClaimForm(request.POST, request.FILES, instance=claim)
        if form.is_valid():
            form.save()
            messages.success(request, 'Insurance claim updated successfully.')
            return redirect('insurance_claim_detail', pk=claim.pk)
    else:
        form = InsuranceClaimForm(instance=claim)
    return render(request, 'hospital/insurance_claim_form.html', {'form': form})

@login_required
def insurance_claim_delete(request, pk):
    claim = get_object_or_404(InsuranceClaim, pk=pk)
    if request.method == 'POST':
        claim.delete()
        messages.success(request, 'Insurance claim deleted successfully.')
        return redirect('insurance_claim_list')
    return render(request, 'hospital/insurance_claim_confirm_delete.html', 
                 {'claim': claim})

def insurance_pdf(request, pk):
    insurance = get_object_or_404(Insurance, pk=pk)
    template_path = 'hospital/insurance_pdf.html'
    context = {'insurance': insurance}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="insurance_{pk}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def insurance_claim_pdf(request, pk):
    claim = get_object_or_404(InsuranceClaim, pk=pk)
    template_path = 'hospital/insurance_claim_pdf.html'
    context = {'claim': claim}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="insurance_claim_{pk}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def hr_dashboard(request):
    departments = Department.objects.all()
    employees = Employee.objects.all()
    leave_requests = LeaveRequest.objects.all().order_by('-created_at')
    pending_leaves = leave_requests.filter(status='pending').count()
    approved_leaves = leave_requests.filter(status='approved').count()
    rejected_leaves = leave_requests.filter(status='rejected').count()

    context = {
        'departments': departments,
        'employees': employees,
        'leave_requests': leave_requests[:5],  # Show only latest 5
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
        'total_employees': employees.count(),
        'total_departments': departments.count(),
    }
    return render(request, 'hospital/hr_dashboard.html', context)

@login_required
def leave_requests(request):
    leave_requests = LeaveRequest.objects.all().order_by('-created_at')
    return render(request, 'hospital/leave_request_list.html', {'leave_requests': leave_requests})

@login_required
def leave_request_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save()
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('leave_request_detail', pk=leave_request.pk)
    else:
        form = LeaveRequestForm()
    return render(request, 'hospital/leave_request_form.html', {'form': form})

@login_required
def leave_request_detail(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    return render(request, 'hospital/leave_request_detail.html', {'leave_request': leave_request})

@login_required
def leave_request_edit(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, instance=leave_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave request updated successfully.')
            return redirect('leave_request_detail', pk=leave_request.pk)
    else:
        form = LeaveRequestForm(instance=leave_request)
    return render(request, 'hospital/leave_request_form.html', {'form': form})

@login_required
def leave_request_delete(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        leave_request.delete()
        messages.success(request, 'Leave request deleted successfully.')
        return redirect('leave_requests')
    return render(request, 'hospital/leave_request_confirm_delete.html', {'leave_request': leave_request})

@login_required
def leave_request_approve(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if leave_request.status == 'pending':
        leave_request.status = 'approved'
        # Try to get the employee associated with the user
        try:
            employee = Employee.objects.get(email=request.user.email)
            leave_request.approved_by = employee
        except Employee.DoesNotExist:
            # If no employee is found, just update the status without setting approved_by
            messages.warning(request, 'Leave request approved, but approver information could not be recorded.')
        leave_request.save()
        messages.success(request, 'Leave request approved successfully.')
    return redirect('leave_request_detail', pk=pk)

@login_required
def leave_request_reject(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if leave_request.status == 'pending':
        leave_request.status = 'rejected'
        leave_request.save()
        messages.success(request, 'Leave request rejected.')
    return redirect('leave_request_detail', pk=pk)

def leave_request_pdf(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    template_path = 'hospital/leave_request_pdf.html'
    context = {'leave_request': leave_request}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="leave_request_{pk}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# Add these views to your views.py

@login_required
def notice_list(request):
    notices = Notice.objects.filter(is_active=True)
    return render(request, 'hospital/notice_list.html', {'notices': notices})

@login_required
def notice_create(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save(commit=False)
            try:
                notice.posted_by = Employee.objects.get(email=request.user.email)
            except Employee.DoesNotExist:
                messages.warning(request, 'Notice created but poster information could not be recorded.')
            notice.save()
            messages.success(request, 'Notice created successfully.')
            return redirect('notice_list')
    else:
        form = NoticeForm()
    return render(request, 'hospital/notice_form.html', {'form': form})

@login_required
def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    return render(request, 'hospital/notice_detail.html', {'notice': notice})

@login_required
def notice_edit(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notice updated successfully.')
            return redirect('notice_detail', pk=pk)
    else:
        form = NoticeForm(instance=notice)
    return render(request, 'hospital/notice_form.html', {'form': form})

@login_required
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        notice.is_active = False
        notice.save()
        messages.success(request, 'Notice deleted successfully.')
        return redirect('notice_list')
    return render(request, 'hospital/notice_confirm_delete.html', {'notice': notice})

@login_required
def report_list(request):
    form = ReportFilterForm(request.GET)
    reports = Report.objects.filter(is_archived=False)
    
    if form.is_valid():
        if form.cleaned_data['report_type']:
            reports = reports.filter(report_type=form.cleaned_data['report_type'])
        if form.cleaned_data['date_from']:
            reports = reports.filter(created_at__date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data['date_to']:
            reports = reports.filter(created_at__date__lte=form.cleaned_data['date_to'])
        if form.cleaned_data['search']:
            reports = reports.filter(
                Q(title__icontains=form.cleaned_data['search']) |
                Q(description__icontains=form.cleaned_data['search'])
            )
    
    return render(request, 'hospital/report_list.html', {
        'reports': reports,
        'filter_form': form
    })

@login_required
def report_create(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            try:
                report.generated_by = Employee.objects.get(email=request.user.email)
            except Employee.DoesNotExist:
                messages.warning(request, 'Report created but generator information could not be recorded.')
            report.save()
            messages.success(request, 'Report created successfully.')
            return redirect('report_list')
    else:
        form = ReportForm()
    return render(request, 'hospital/report_form.html', {'form': form})

@login_required
def report_detail(request, pk):
    report = get_object_or_404(Report, pk=pk)
    return render(request, 'hospital/report_detail.html', {'report': report})

@login_required
def report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Report deleted successfully.')
        return redirect('report_list')
    return redirect('report_list')

@login_required
def report_download(request, pk):
    report = get_object_or_404(Report, pk=pk)
    response = FileResponse(report.file)
    response['Content-Disposition'] = f'attachment; filename="{report.file.name}"'
    return response

@login_required
def report_edit(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            report = form.save()
            messages.success(request, 'Report updated successfully.')
            return redirect('report_detail', pk=report.pk)
    else:
        form = ReportForm(instance=report)
    return render(request, 'hospital/report_form.html', {'form': form, 'report': report})