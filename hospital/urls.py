from django.urls import path
from . import views
from .views import LabTestListView, LabTestCreateView, LabTestUpdateView,\
     LabTestDeleteView, LabTestDetailView

urlpatterns = [
    # Registration URL
    path('', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboard URL
    path('dashboard/', views.dashboard, name='dashboard'),

    # Patient URLs
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.patient_add, name='patient_add'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_edit, name='patient_edit'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('patients/<int:pk>/admit/', views.admit_patient, name='admit_patient'),
    path('patients/<int:patient_id>/pdf/', views.patient_pdf, 
         name='patient_pdf'),

    # Employee URLs
    path('employees/', views.employee_list, 
         name='employee_list'),
    path('employees/add/', views.employee_add,
          name='employee_add'),
    path('employees/<int:pk>/', views.employee_detail, 
         name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, 
         name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, 
         name='employee_delete'),
    path('employees/<int:employee_id>/pdf/', views.employee_pdf, 
         name='employee_pdf'),

    # Doctor URLs
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/add/', views.doctor_add, name='doctor_add'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/<int:pk>/edit/', views.doctor_edit, name='doctor_edit'),
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    path('doctors/<int:doctor_id>/pdf/', views.doctor_pdf, 
         name='doctor_pdf'),

    # Appointment URLs
    path('appointments/', views.appointment_list, 
         name='appointment_list'),
    path('appointments/add/', views.appointment_add, 
         name='appointment_add'),
    path('appointments/<int:pk>/', views.appointment_detail,
          name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.appointment_edit, 
         name='appointment_edit'),
    path('appointments/<int:pk>/delete/', views.appointment_delete, 
         name='appointment_delete'),
    path('appointments/<int:appointment_id>/pdf/', views.appointment_pdf, 
         name='appointment_pdf'),
    
    # Ward URLs
    path('wards/', views.ward_list, name='ward_list'),
    path('wards/<int:pk>/', views.ward_detail, name='ward_detail'),
    path('wards/create/', views.ward_create, name='ward_create'),
    path('wards/<int:pk>/update/', views.ward_update, name='ward_update'),
    path('wards/<int:pk>/delete/', views.ward_delete, name='ward_delete'),
    path('wards/<int:ward_id>/pdf/', views.ward_pdf, 
         name='ward_pdf'),

    # Bed URLs
    path('beds/', views.bed_list, name='bed_list'),
    path('beds/<int:pk>/', views.bed_detail, name='bed_detail'),
    path('beds/create/', views.bed_create, name='bed_create'),
    path('beds/<int:pk>/update/', views.bed_update, name='bed_update'),
    path('patients/<int:patient_id>/assign_bed/', views.assign_bed, 
         name='assign_bed'),
    path('beds/<int:pk>/delete/', views.bed_delete, name='bed_delete'),
    path('beds/<int:bed_id>/pdf/', views.bed_pdf, name='bed_pdf'),


    # OT Booking URLs
    path('ot-bookings/', views.ot_booking_list, name='ot_booking_list'),
    path('ot-bookings/create/', views.ot_booking_create, name='ot_booking_create'),
    path('ot-bookings/<int:pk>/update/', views.ot_booking_update, 
         name='ot_booking_update'),
    path('ot-bookings/<int:pk>/delete/', views.ot_booking_delete, 
         name='ot_booking_delete'),
    path('ot-bookings/<int:pk>/', views.ot_booking_detail, 
         name='ot_booking_detail'),
    path('ot-bookings/<int:booking_id>/pdf/', views.ot_booking_pdf, 
         name='ot_booking_pdf'),

    # Account Management URLs
    path('account/', views.account_management, name='account_management'),
    path('account/change-password/', views.change_password, name='change_password'),
    path('account/profile/', views.profile, name='profile'),
    path('account/view-profile/', views.view_profile, name='view_profile'),

    # Payroll URL
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/add/', views.payroll_add, name='payroll_add'),
    path('payroll/<int:pk>/edit/', views.payroll_edit, name='payroll_edit'),
    path('payroll/<int:pk>/', views.payroll_view, name='payroll_view'),
    path('payroll/<int:pk>/delete/', views.payroll_delete, name='payroll_delete'),
    path('payroll/<int:payroll_id>/pdf/', views.payroll_pdf, name='payroll_pdf'),

    # Patient Billing URLs
    path('patient-billing/', views.patient_billing_list, 
         name='patient_billing_list'),
    path('patient-billing/add/', views.patient_billing_add,
          name='patient_billing_add'),
    path('patient-billing/<int:pk>/', views.patient_billing_view, 
         name='patient_billing_view'),
    path('patient-billing/<int:pk>/edit/', views.patient_billing_edit, 
         name='patient_billing_edit'),
    path('patient-billing/<int:pk>/delete/', views.patient_billing_delete, 
         name='patient_billing_delete'),
    path('patient-billing/<int:patient_billing_id>/pdf/', views.patient_billing_pdf, 
         name='patient_billing_pdf'),

    # Pharmacy Management URLs
    path('medications/', views.MedicationListView.as_view(), 
         name='medication_list'),
    path('medications/create/', views.MedicationCreateView.as_view(), 
         name='medication_create'),
    path('medications/<int:pk>/', views.MedicationDetailView.as_view(), 
         name='medication_detail'),
    path('medications/<int:pk>/update/', views.MedicationUpdateView.as_view(), 
         name='medication_update'),
    path('medications/<int:pk>/delete/', views.MedicationDeleteView.as_view(), 
         name='medication_delete'),
    path('medications/<int:medication_id>/pdf/', views.medication_pdf, 
         name='medication_pdf'),
    
    path('prescriptions/', views.PrescriptionListView.as_view(), 
         name='prescription_list'),
    path('prescriptions/create/', views.PrescriptionCreateView.as_view(), 
         name='prescription_create'),
    path('prescriptions/<int:pk>/update/', views.PrescriptionUpdateView.as_view(),
         name='prescription_update'),
    path('prescriptions/<int:pk>/fill/', views.fill_prescription, 
         name='fill_prescription'),
    path('prescriptions/<int:pk>/', views.PrescriptionDetailView.as_view(), 
         name='prescription_detail'),
    path('prescriptions/<int:pk>/delete/', views.PrescriptionDeleteView.as_view(), 
         name='prescription_delete'),
    path('prescriptions/<int:prescription_id>/pdf/', views.prescription_pdf, 
         name='prescription_pdf'),

    # Ambulance Management URLs
    path('ambulances/', views.AmbulanceListView.as_view(), name='ambulance_list'),
    path('ambulances/<int:pk>/', views.AmbulanceDetailView.as_view(), 
         name='ambulance_detail'),
    path('ambulances/create/', views.AmbulanceCreateView.as_view(), 
         name='ambulance_create'),
    path('ambulances/<int:pk>/update/', views.AmbulanceUpdateView.as_view(), 
         name='ambulance_update'),
    path('ambulances/<int:pk>/delete/', views.AmbulanceDeleteView.as_view(), 
         name='ambulance_delete'),
    path('ambulances/<int:ambulance_id>/pdf/', views.ambulance_pdf, 
         name='ambulance_pdf'),
    
    path('assign-ambulance/', views.assign_ambulance, name='assign_ambulance'),
    path('assignment/<int:pk>/', views.assignment_detail, name='assignment_detail'),

    # Patient Serial URLs
    path('patient-serials/', views.patient_serial_list, name='patient_serial_list'),
    path('patient-serials/create/', views.create_patient_serial, 
         name='create_patient_serial'),
    path('patient-serials/<int:pk>/', views.patient_serial_detail, 
         name='patient_serial_detail'),
    path('patient-serials/<int:pk>/edit/', views.edit_patient_serial, 
         name='edit_patient_serial'),
    path('patient-serials/<int:pk>/delete/', views.delete_patient_serial, 
         name='delete_patient_serial'),
    path('patient-serials/<int:pk>/update-status/', views.update_patient_serial_status, 
         name='update_patient_serial_status'),
    path('patient-serials/<int:serial_id>/pdf/', views.patient_serial_pdf, 
         name='patient_serial_pdf'),

    # Lab Test URLs
    path('lab-tests/', LabTestListView.as_view(), 
         name='lab_test_list'),
    path('lab-tests/add/', LabTestCreateView.as_view(), 
         name='lab_test_add'),
    path('lab-tests/<int:pk>/', LabTestDetailView.as_view(), 
         name='lab_test_detail'),
    path('lab-tests/<int:pk>/edit/', LabTestUpdateView.as_view(), 
         name='lab_test_edit'),
    path('lab-tests/<int:pk>/delete/', LabTestDeleteView.as_view(), 
         name='lab_test_delete'),
    path('lab-tests/<int:pk>/complete/', views.complete_lab_test, 
         name='complete_lab_test'),
    path('lab-tests/<int:lab_test_id>/pdf/', views.lab_test_pdf, 
         name='lab_test_pdf'),
    path('opd/appointments/', views.opd_appointment_list, 
         name='opd_appointment_list'),
    path('opd/appointments/<int:pk>/', views.opd_appointment_detail, 
         name='opd_appointment_detail'),
    path('opd/appointments/create/', views.opd_appointment_create, 
         name='opd_appointment_create'),
    path('opd/appointments/<int:pk>/edit/', views.opd_appointment_edit, 
         name='opd_appointment_edit'),
    path('opd/appointments/<int:pk>/delete/', views.opd_appointment_delete, 
         name='opd_appointment_delete'),
    path('opd/appointments/<int:appointment_id>/pdf/', views.opd_appointment_pdf, 
         name='opd_appointment_pdf'),

    # IPD URLs
    path('ipd/admissions/', views.ipd_admission_list, 
         name='ipd_admission_list'),
    path('ipd/admissions/create/', views.ipd_admission_create, 
         name='ipd_admission_create'),
    path('ipd/admissions/<int:pk>/', views.ipd_admission_detail, 
         name='ipd_admission_detail'),
    path('ipd/admissions/<int:pk>/edit/', views.ipd_admission_edit, 
         name='ipd_admission_edit'),
    path('ipd/admissions/<int:pk>/discharge/', views.ipd_admission_discharge, 
         name='ipd_admission_discharge'),
    path('ipd/admissions/<int:admission_id>/pdf/', views.ipd_admission_pdf, 
         name='ipd_admission_pdf'),

    # Insurance URLs
    path('insurance/', views.insurance_list, name='insurance_list'),
    path('insurance/create/', views.insurance_create, name='insurance_create'),
    path('insurance/<int:pk>/', views.insurance_detail, name='insurance_detail'),
    path('insurance/<int:pk>/edit/', views.insurance_edit, name='insurance_edit'),
    path('insurance/<int:pk>/delete/', views.insurance_delete, name='insurance_delete'),
    path('insurance/<int:pk>/pdf/', views.insurance_pdf, name='insurance_pdf'),

    path('insurance-claims/', views.insurance_claim_list, name='insurance_claim_list'),
    path('insurance-claims/create/', views.insurance_claim_create, name='insurance_claim_create'),
    path('insurance-claims/<int:pk>/', views.insurance_claim_detail, name='insurance_claim_detail'),
    path('insurance-claims/<int:pk>/edit/', views.insurance_claim_edit, name='insurance_claim_edit'),
    path('insurance-claims/<int:pk>/delete/', views.insurance_claim_delete, name='insurance_claim_delete'),
    path('insurance-claims/<int:pk>/pdf/', views.insurance_claim_pdf, name='insurance_claim_pdf'),

    # HR URLs
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/leave-requests/', views.leave_requests, name='leave_requests'),
    path('hr/leave-requests/create/', views.leave_request_create, name='leave_request_create'),
    path('hr/leave-requests/<int:pk>/', views.leave_request_detail, name='leave_request_detail'),
    path('hr/leave-requests/<int:pk>/edit/', views.leave_request_edit, name='leave_request_edit'),
    path('hr/leave-requests/<int:pk>/delete/', views.leave_request_delete, name='leave_request_delete'),
    path('hr/leave-requests/<int:pk>/approve/', views.leave_request_approve, name='leave_request_approve'),
    path('hr/leave-requests/<int:pk>/reject/', views.leave_request_reject, name='leave_request_reject'),
    path('hr/leave-requests/<int:pk>/pdf/', views.leave_request_pdf, name='leave_request_pdf'),

    # Notice Board URLs
    path('notices/', views.notice_list, name='notice_list'),
    path('notices/create/', views.notice_create, name='notice_create'),
    path('notices/<int:pk>/', views.notice_detail, name='notice_detail'),
    path('notices/<int:pk>/edit/', views.notice_edit, name='notice_edit'),
    path('notices/<int:pk>/delete/', views.notice_delete, name='notice_delete'),

    # Reports URLs
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    path('reports/<int:pk>/edit/', views.report_edit, name='report_edit'),
    path('reports/create/', views.report_create, name='report_create'),
    path('reports/<int:pk>/delete/', views.report_delete, name='report_delete'),
    path('reports/<int:pk>/download/', views.report_download, name='report_download'),

    # Nurse URLs
    path('nurses/', views.nurse_list, name='nurse_list'),
    path('nurses/create/', views.nurse_create, name='nurse_create'),
    path('nurses/<int:pk>/', views.nurse_detail, name='nurse_detail'),
    path('nurses/<int:pk>/edit/', views.nurse_edit, name='nurse_edit'),
    path('nurses/<int:pk>/delete/', views.nurse_delete, name='nurse_delete'),
    path('nurses/<int:pk>/assign-ward/', views.assign_nurse_ward, name='assign_nurse_ward'),
    path('nurses/<int:pk>/pdf/', views.nurse_pdf, name='nurse_pdf'),
]
