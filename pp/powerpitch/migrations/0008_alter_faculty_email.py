# Generated by Django 5.1.4 on 2024-12-22 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerpitch', '0007_faculty_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faculty',
            name='Email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]