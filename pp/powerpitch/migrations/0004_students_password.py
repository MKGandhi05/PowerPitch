# Generated by Django 5.1.4 on 2024-12-22 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerpitch', '0003_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='Password',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]