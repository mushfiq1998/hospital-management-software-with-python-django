# Generated by Django 4.2.16 on 2024-11-06 13:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hospital', '0017_patient_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Inventory Categories',
            },
        ),
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('unit', models.CharField(choices=[('piece', 'Piece'), ('box', 'Box'), ('carton', 'Carton'), ('packet', 'Packet'), ('bottle', 'Bottle'), ('vial', 'Vial'), ('ampule', 'Ampule'), ('kg', 'Kilogram'), ('g', 'Gram'), ('mg', 'Milligram'), ('ml', 'Milliliter'), ('l', 'Liter')], max_length=20)),
                ('quantity', models.IntegerField(default=0)),
                ('reorder_level', models.IntegerField(default=10)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('supplier', models.CharField(blank=True, max_length=200)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='hospital.inventorycategory')),
            ],
        ),
        migrations.CreateModel(
            name='InventoryTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('in', 'Stock In'), ('out', 'Stock Out'), ('adjust', 'Adjustment')], max_length=10)),
                ('quantity', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('reference', models.CharField(blank=True, max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospital.inventoryitem')),
                ('performed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='patient',
            name='user',
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
    ]