from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class StrAsModelName(models.Model):
    name = models.CharField(verbose_name='Nome', max_length=50)

    def __str__(self):
        return self.name


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

    def get_classes(self):
        if hasattr(self, 'student'):
            return self.student.classes.all()
        elif hasattr(self, 'professor'):
            return CourseClass.objects.filter(teacher=self.professor)
        else:
            return CourseClass.objects.none()


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


class CourseClass(StrAsModelName):
    year = models.IntegerField(verbose_name='Ano')
    semester = models.IntegerField(verbose_name='Semestre', choices=[(1, 1), (2, 3)])
    professor = models.ForeignKey(Professor, verbose_name='Professor', on_delete=models.RESTRICT,
                                  related_name='classes')

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.RESTRICT, verbose_name='Usuário')
    registration_number = models.IntegerField(verbose_name='Matrícula', unique=True,
                                              help_text='Digite a matrícula somente com números. '
                                                        'Ex 160123456')
    classes = models.ManyToManyField(CourseClass, verbose_name='Turmas', blank=True, related_name='students')

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'

    def __str__(self):
        return self.user.full_name

    def clean(self):
        if Professor.objects.filter(user=self.user).exists():
            raise ValidationError('Este usuário já é um professor.')


class Question(StrAsModelName):
    class Subjects(models.IntegerChoices):
        SEQ = 0, "ESTRUTURAS SEQUENCIAIS E CONDICIONAIS"
        MOD = 1, "MODULARIZAÇÃO"
        COND = 2, "ESTRUTURAS CONDICIONAIS E DE REPETIÇÃO"
        VET = 4, "VETORES"

    description = models.TextField(verbose_name='Enunciado')
    subject = models.CharField(verbose_name='Assunto', choices=Subjects.choices, max_length=60)

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'


class TestCase(models.Model):
    inputs = models.TextField(verbose_name='Entradas',
                              help_text='Cada entrada separada por vírgula e em ordem de leitura.')
    output = models.TextField(verbose_name='Saída',
                              help_text='String única com \\n explícito se necessário.')
    question = models.ForeignKey(Question, verbose_name='Questão', on_delete=models.CASCADE, related_name='cases')

    class Meta:
        verbose_name = 'Caso de Teste'
        verbose_name_plural = 'Casos de Teste'

    def __str__(self):
        return self.question.name + '-Saída:' + self.output


class QuestionList(StrAsModelName):
    questions = models.ManyToManyField(Question, verbose_name='Questões', related_name='lists')

    class Meta:
        verbose_name = 'Lista de Exercícios'
        verbose_name_plural = 'Listas de Exercicíos'


class QuestionListApplication(StrAsModelName):
    start_date = models.DateTimeField(verbose_name="Data de Início", auto_now=False, auto_now_add=False)
    due_date = models.DateTimeField(verbose_name="Data de Término", auto_now=False, auto_now_add=False)
    course_class = models.ForeignKey(CourseClass, verbose_name='Turma', on_delete=models.RESTRICT,
                                     related_name='applications')
    question_list = models.ForeignKey(QuestionList, verbose_name='Lista de Exercícios',
                                      on_delete=models.RESTRICT, related_name='applications')

    class Meta:
        verbose_name = 'Agendamento de Lista'
        verbose_name_plural = 'Agendamentos de Listas'

    def student_has_concluded(self, student):
        questions = self.question_list.questions
        submissions = Submission.objects.filter(student=student, question__in=questions.all())
        return questions.count() == submissions.count()


class Submission(models.Model):
    class Results(models.IntegerChoices):
        ACCEPTED = 0, "Aceito"
        WRONG_ANSWER = 1, "Resposta Incorreta"
        PRESENTATION_ERROR = 2, "Erro de Apresentação"
        COMPILATION_ERROR = 3, "Erro de Compilação"
        RUNTIME_ERROR = 4, "Erro de Execução"
        TIME_LIMIT_EXCEEDED = 5, "Limite de Tempo Excedido"
        MEMORY_LIMIT_EXCEEDED = 6, "Limite de Memória Excedido"
        POSSIBLE_RUNTIME_ERROR = 7, "Possível Erro de Execução"

    question = models.ForeignKey(Question, verbose_name='Questão', on_delete=models.RESTRICT, related_name='submissions')
    student = models.ForeignKey(Student, verbose_name='Aluno', on_delete=models.RESTRICT, related_name='submissions')
    code = models.TextField(verbose_name="Código")
    submitted_at = models.DateTimeField(verbose_name='Submetido em', auto_now_add=True, editable=False)
    judged_at = models.DateTimeField(verbose_name='Julgado em', blank=True, editable=False, null=True)
    result = models.CharField(verbose_name='Resultado', max_length=30, blank=True, null=True, editable=False,
                              choices=Results.choices)

    class Meta:
        verbose_name = 'Submissão'
        verbose_name_plural = 'Submissões'

    def __str__(self):
        return '#' + str(self.pk)
