# Generated by Django 4.2.16 on 2024-10-30 13:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0009_remove_doctor_joining_date_remove_doctor_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ipdadmission',
            name='bed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hospital.bed'),
        ),
        migrations.AddField(
            model_name='ipdadmission',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
