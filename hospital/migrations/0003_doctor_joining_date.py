# Generated by Django 4.2.16 on 2024-10-23 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0002_employee_joining_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='joining_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]