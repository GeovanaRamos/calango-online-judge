from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class CustomUserManager(BaseUserManager):

    def create_user(self, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError('É preciso informar um email.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    full_name = models.CharField(verbose_name="Nome completo", max_length=70)
    email = models.EmailField(verbose_name="Email", unique=True)
    username = None
    first_name = None
    last_name = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.full_name


class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.RESTRICT, verbose_name='Usuário')

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'

    def __str__(self):
        return self.user.full_name

    def clean(self):
        if Student.objects.filter(user=self.user).exists():
            raise ValidationError('Este usuário já é um aluno.')


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.RESTRICT, verbose_name='Usuário')
    registration_number = models.IntegerField(verbose_name='Matrícula', unique=True,
                                              help_text='Digite a matrícula somente com números. '
                                                        'Ex 160123456')
    classes = models.ManyToManyField('judge.CourseClass', verbose_name='Turmas', blank=True, related_name='students')

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'

    def __str__(self):
        return self.user.full_name

    def clean(self):
        if Professor.objects.filter(user=self.user).exists():
            raise ValidationError('Este usuário já é um professor.')
