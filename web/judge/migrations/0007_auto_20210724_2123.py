# Generated by Django 3.1.4 on 2021-07-25 00:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0006_remove_courseclass_students'),
    ]

    operations = [
        migrations.RenameField(
            model_name='courseclass',
            old_name='students2',
            new_name='students',
        ),
    ]
