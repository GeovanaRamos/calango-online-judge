# Generated by Django 3.1.14 on 2022-07-28 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0009_courseclass_is_synthesis_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseclass',
            name='discipline',
            field=models.CharField(choices=[('TESTE', 'Teste'), ('APC', 'Algoritmos e Programação para Computadores'), ('APC-MONITORIA', 'Monitoria de APC')], max_length=50, verbose_name='Disciplina'),
        ),
    ]