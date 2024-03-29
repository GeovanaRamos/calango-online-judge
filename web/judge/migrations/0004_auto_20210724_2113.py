# Generated by Django 3.1.4 on 2021-07-25 00:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_student_first_login'),
        ('judge', '0003_auto_20210706_2110'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_login', models.DateTimeField(blank=True, null=True, verbose_name='Primeiro Login')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='Último Login')),
                ('course_class', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='judge.courseclass', verbose_name='Turma')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='accounts.student', verbose_name='Aluno')),
            ],
            options={
                'verbose_name': 'Matrícula em Turma',
                'verbose_name_plural': 'Matrículas em Turma',
                'unique_together': {('student', 'course_class')},
            },
        ),
        migrations.AddField(
            model_name='courseclass',
            name='students2',
            field=models.ManyToManyField(blank=True, through='judge.Enrollment', to='accounts.Student', verbose_name='Alunos'),
        ),
    ]
