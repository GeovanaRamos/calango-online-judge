# Generated by Django 3.1.4 on 2021-07-25 11:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_student_first_login'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='first_login',
        ),
    ]