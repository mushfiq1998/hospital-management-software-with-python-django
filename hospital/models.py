from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.urls import reverse

class Employee(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.position}"


class Ward(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name


class Bed(models.Model):
    number = models.CharField(max_length=10)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='beds')
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"Bed {self.number} in {self.ward.name}"


class Patient(models.Model):
    PATIENT_TYPES = [
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
    ]
    name = models.CharField(max_length=200, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True,
                    choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='patient_photos/', null=True, blank=True)
    patient_type = models.CharField(max_length=7, 
                                    choices=PATIENT_TYPES, default='outdoor')
    is_admitted = models.BooleanField(default=False)
    admission_date = models.DateTimeField(null=True, blank=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    bed = models.OneToOneField(Bed, on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='current_patient')

    def __str__(self):
        return self.name


class Doctor(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE,
                        related_name='doctor', blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.get_name()

    def get_name(self):
        if self.employee:
            return f"Dr. {self.employee.name}"
        return "Doctor (No Name)"

    def get_phone(self):
        if self.employee:
            return self.employee.phone_number
        return None

    def get_joining_date(self):
        if self.employee:
            return self.employee.joining_date
        return None

    def get_photo_url(self):
        if self.employee and self.employee.photo:
            return self.employee.photo.url
        return None


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()

    def __str__(self):
        return f"{self.patient.name} - {self.doctor.get_name()} - {self.date} {self.time}"


class OTBooking(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    procedure = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.patient.name} - {self.procedure} - {self.scheduled_time}"

    @property
    def is_ongoing(self):
        return self.status == 'in_progress'

    @property
    def is_upcoming(self):
        return self.status == 'scheduled' and self.scheduled_time > timezone.now()


class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pay_date = models.DateField()
    
    def total_pay(self):
        return self.salary + self.bonus - self.deductions

    def __str__(self):
        return f"{self.employee.username} - {self.pay_date}"


class PatientBilling(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='billings')
    billing_date = models.DateTimeField(default=timezone.now)
    admission_date = models.DateTimeField(null=True, blank=True)
    release_date = models.DateTimeField(null=True, blank=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Billing for {self.patient.name} - {self.billing_date.date()}"

    def calculate_total_amount(self):
        if self.admission_date and self.release_date:
            days = (self.release_date - self.admission_date).days
            return self.daily_rate * days
        return 0

    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.calculate_total_amount()
        super().save(*args, **kwargs)


class Medication(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, default='Unknown')  # Add default value
    action = models.TextField(blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Prescription(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    diseases = models.TextField(blank=True)
    date_prescribed = models.DateField(auto_now_add=True)
    is_filled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patient} - {self.date_prescribed}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, related_name='items', 
                                     on_delete=models.CASCADE)
    medication = models.ForeignKey('Medication', on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.prescription} - {self.medication}"


class Ambulance(models.Model):
    vehicle_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_call', 'On Call'),
        ('maintenance', 'Under Maintenance'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                              default='available')
    last_maintenance = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='ambulance_photos/', 
                              null=True, blank=True) 

    def __str__(self):
        return f"Ambulance {self.vehicle_number}"


class AmbulanceAssignment(models.Model):
    ASSIGNMENT_STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    ambulance = models.ForeignKey(Ambulance, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, 
                              default='assigned')

    def __str__(self):
        return f"Ambulance {self.ambulance.vehicle_number} assigned to {self.patient.name}"

    def save(self, *args, **kwargs):
        if self.pk is None:  # New assignment
            self.ambulance.status = 'on_call'
            self.ambulance.save()
        super().save(*args, **kwargs)


class Communication(models.Model):
    assignment = models.ForeignKey(AmbulanceAssignment, 
                    on_delete=models.CASCADE, related_name='communications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Communication for {self.assignment} at {self.timestamp}"


class PatientSerial(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE,
                                blank=True, null=True)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE,
                                blank=True, null=True)
    date = models.DateField(default=timezone.now)
    serial_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                              default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'serial_number']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'date', 'serial_number'],
                name='unique_doctor_date_serial'
            )
        ]

    def __str__(self):
        patient_name = self.patient.name if self.patient else "No Patient"
        doctor_name = self.doctor.get_name() if self.doctor else "No Doctor"
        return f"Serial {self.serial_number} - {patient_name} - {doctor_name}"

    @property
    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]


class LabTest(models.Model):
    TEST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    test_name = models.CharField(max_length=200)
    test_description = models.TextField(blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TEST_STATUS_CHOICES, default='pending')
    results = models.TextField(blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='ordered_tests')

    def __str__(self):
        return f"{self.test_name} for {self.patient.name}"

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    head = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_department')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class OPDAppointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='scheduled')

    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.appointment_date}"

class IPDAdmission(models.Model):
    STATUS_CHOICES = [
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged')
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    admission_date = models.DateTimeField()
    discharge_date = models.DateTimeField(null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                              default='admitted')
    bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, 
                            null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.patient.name} - {self.admission_date}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]

class Insurance(models.Model):
    INSURANCE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('pending', 'Pending Approval'),
        ('rejected', 'Rejected'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, 
                                related_name='insurances')
    policy_number = models.CharField(max_length=50, unique=True)
    provider_name = models.CharField(max_length=100, null=True, blank=True)
    policy_type = models.CharField(max_length=100, null=True, blank=True)
    coverage_amount = models.DecimalField(max_digits=10, decimal_places=2, 
                                          null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, 
                              choices=INSURANCE_STATUS_CHOICES, 
                              default='pending')
    documents = models.FileField(upload_to='insurance_documents/', 
                                 null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.name} - {self.policy_number}"

    def is_valid(self):
        today = timezone.now().date()
        return (self.status == 'active' and 
                self.start_date <= today <= self.end_date)

    def remaining_coverage(self):
        used_amount = self.claims.aggregate(
            total=models.Sum('claimed_amount'))['total'] or 0
        return self.coverage_amount - used_amount

class InsuranceClaim(models.Model):
    CLAIM_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]

    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, 
                                  related_name='claims')
    patient_billing = models.ForeignKey(PatientBilling, 
                    on_delete=models.CASCADE, null=True, blank=True   )
    claim_number = models.CharField(max_length=50, unique=True)
    claimed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, 
                                           null=True, blank=True)
    status = models.CharField(max_length=20, choices=CLAIM_STATUS_CHOICES, 
                              default='pending')
    filed_date = models.DateField(auto_now_add=True)
    processed_date = models.DateField(null=True, blank=True)
    documents = models.FileField(upload_to='claim_documents/', 
                                  null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Claim {self.claim_number} - {self.insurance.patient.name}"

    def save(self, *args, **kwargs):
        if not self.claim_number:
            # Generate a unique claim number
            prefix = 'CLM'
            last_claim = InsuranceClaim.objects.order_by('-id').first()
            if last_claim:
                last_number = int(last_claim.claim_number[3:])
                self.claim_number = f"{prefix}{str(last_number + 1).zfill(6)}"
            else:
                self.claim_number = f"{prefix}000001"
        super().save(*args, **kwargs)

class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('marriage', 'Marriage Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, 
                                 related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                                default='pending')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, 
                        null=True, blank=True, related_name='approved_leaves')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    marriage_certificate = models.FileField(upload_to='marriage_certificates/', 
                                          null=True, blank=True)

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type} ({self.start_date} to {self.end_date})"

    def duration(self):
        return (self.end_date - self.start_date).days + 1


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, 
                                 related_name='attendance')
    date = models.DateField(null=True, blank=True)
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
    ])
    notes = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.name} - {self.date}"

class Performance(models.Model):
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, 
                                 related_name='performance_reviews')
    review_date = models.DateField(null=True, blank=True)
    reviewer = models.ForeignKey(Employee, on_delete=models.SET_NULL, 
                                 null=True, related_name='reviews_given')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField(null=True, blank=True)
    goals = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.name} - {self.review_date}"

class Training(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    trainer = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    participants = models.ManyToManyField(Employee, related_name='trainings')
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Notice(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    expiry_date = models.DateField(null=True, blank=True)
    attachment = models.FileField(upload_to='notice_attachments/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Report(models.Model):
    REPORT_TYPES = (
        ('lab', 'Laboratory Report'),
        ('rad', 'Radiology Report'),
        ('path', 'Pathology Report'),
        ('op', 'Operation Report'),
        ('dis', 'Discharge Summary'),
        ('prog', 'Progress Report'),
    )

    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, 
                              related_name='reports', null=True, blank=True)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, 
                             related_name='reports', null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, 
                                 related_name='reports', null=True, blank=True)
    diagnosis = models.TextField(null=True, blank=True)
    treatment_plan = models.TextField(null=True, blank=True)
    prescriptions = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        patient_name = self.patient.name if self.patient else "No Patient"
        return f"{self.title} - {patient_name} ({self.get_report_type_display()})"

class ReportAttachment(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='report_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
