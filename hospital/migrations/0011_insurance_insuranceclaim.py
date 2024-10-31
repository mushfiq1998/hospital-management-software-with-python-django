# Generated by Django 4.2.16 on 2024-10-31 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0010_ipdadmission_bed_ipdadmission_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Insurance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('policy_number', models.CharField(max_length=50, unique=True)),
                ('provider_name', models.CharField(blank=True, max_length=100, null=True)),
                ('policy_type', models.CharField(blank=True, max_length=100, null=True)),
                ('coverage_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('pending', 'Pending Approval'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('documents', models.FileField(blank=True, null=True, upload_to='insurance_documents/')),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='insurances', to='hospital.patient')),
            ],
        ),
        migrations.CreateModel(
            name='InsuranceClaim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('claim_number', models.CharField(max_length=50, unique=True)),
                ('claimed_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('approved_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('paid', 'Paid')], default='pending', max_length=20)),
                ('filed_date', models.DateField(auto_now_add=True)),
                ('processed_date', models.DateField(blank=True, null=True)),
                ('documents', models.FileField(blank=True, null=True, upload_to='claim_documents/')),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('insurance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claims', to='hospital.insurance')),
                ('patient_billing', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hospital.patientbilling')),
            ],
        ),
    ]
