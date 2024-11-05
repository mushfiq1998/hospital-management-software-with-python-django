# Generated by Django 4.2.16 on 2024-11-05 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0014_remove_report_description_remove_report_generated_by_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nurse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialization', models.CharField(blank=True, max_length=100, null=True)),
                ('shift', models.CharField(choices=[('morning', 'Morning Shift'), ('evening', 'Evening Shift'), ('night', 'Night Shift')], default='morning', max_length=20)),
                ('is_on_duty', models.BooleanField(default=False)),
                ('license_number', models.CharField(max_length=50, unique=True)),
                ('experience_years', models.PositiveIntegerField(default=0)),
                ('additional_skills', models.TextField(blank=True)),
                ('assigned_ward', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hospital.ward')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hospital.department')),
                ('employee', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='nurse', to='hospital.employee')),
            ],
            options={
                'ordering': ['employee__name'],
            },
        ),
    ]