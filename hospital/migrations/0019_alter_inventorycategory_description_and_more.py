# Generated by Django 4.2.16 on 2024-11-06 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0018_inventorycategory_inventoryitem_inventorytransaction_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorycategory',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='supplier',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='unit',
            field=models.CharField(blank=True, choices=[('piece', 'Piece'), ('box', 'Box'), ('carton', 'Carton'), ('packet', 'Packet'), ('bottle', 'Bottle'), ('vial', 'Vial'), ('ampule', 'Ampule'), ('kg', 'Kilogram'), ('g', 'Gram'), ('mg', 'Milligram'), ('ml', 'Milliliter'), ('l', 'Liter')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='unit_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
