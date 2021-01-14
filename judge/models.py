from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import RESTRICT, CASCADE
from django.utils import timezone

from accounts.models import User, Professor, Student


class CourseClass(models.Model):
    class Disciplines(models.TextChoices):
        TEST = 'TESTE', "Teste"
        APC = 'APC', "Algoritmos e Programação para Computadores"

    discipline = models.CharField(verbose_name='Disciplina', max_length=50, choices=Disciplines.choices)
    year = models.PositiveSmallIntegerField(verbose_name='Ano')
    semester = models.PositiveSmallIntegerField(verbose_name='Semestre', choices=[(1, 1), (2, 2)])
    professor = models.ForeignKey(Professor, verbose_name='Professor', on_delete=RESTRICT, related_name='classes')
    is_active = models.BooleanField(verbose_name='Ativa?', default=True)
    students = models.ManyToManyField(Student, verbose_name='Alunos', blank=True, related_name='classes')

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        unique_together = ('discipline', 'year', 'semester')

    def __str__(self):
        return self.discipline + ' - ' + str(self.year) + '/' + str(self.semester)


class Question(models.Model):
    class Subjects(models.TextChoices):
        SEQUENCE = 'Sequenciais', "Estruturas Sequenciais"
        CONDITION = 'Condicionais', "Estruturas Condicionais"
        MODULE = 'Modularização', "Modularização"
        REPETITION = 'Repetição', "Estruturas de Repetição"
        VECTOR = 'Vetores', "Vetores"

    name = models.CharField(verbose_name='Nome', max_length=35)
    description = models.TextField(verbose_name='Enunciado')
    subject = models.CharField(verbose_name='Assunto', choices=Subjects.choices, max_length=40)
    author = models.ForeignKey(Professor, verbose_name='Autor', on_delete=RESTRICT, related_name='questions')

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'

    def __str__(self):
        return self.name


class TestCase(models.Model):
    inputs = models.TextField(verbose_name='Entradas')
    output = models.TextField(verbose_name='Saída')
    question = models.ForeignKey(Question, verbose_name='Questão', on_delete=CASCADE, related_name='cases')

    class Meta:
        verbose_name = 'Caso de Teste'
        verbose_name_plural = 'Casos de Teste'

    def __str__(self):
        return self.question.name + '-Saída:' + self.output


class QuestionList(models.Model):
    name = models.CharField(verbose_name='Nome da Lista', max_length=50)
    questions = models.ManyToManyField(Question, verbose_name='Questões', related_name='lists')

    class Meta:
        verbose_name = 'Lista de Exercícios'
        verbose_name_plural = 'Listas de Exercicíos'

    def __str__(self):
        return self.name


class ListSchedule(models.Model):
    start_date = models.DateTimeField(verbose_name="Data de Início", auto_now=False, auto_now_add=False)
    due_date = models.DateTimeField(verbose_name="Data de Término", auto_now=False, auto_now_add=False)
    course_class = models.ForeignKey(CourseClass, verbose_name='Turma', on_delete=RESTRICT, related_name='schedules')
    question_list = models.ForeignKey(QuestionList, verbose_name='Lista de Exercícios', on_delete=RESTRICT,
                                      related_name='schedules')

    class Meta:
        verbose_name = 'Agendamento de Lista'
        verbose_name_plural = 'Agendamentos de Listas'

    def __str__(self):
        return self.question_list.name + ' - ' + self.course_class.__str__()

    def clean(self):
        if self.due_date < self.start_date:
            raise ValidationError('A data de término deve ser posterior a de início.')
        elif self.start_date < timezone.localtime():
            raise ValidationError('A data de ínicio deve ser igual ou posterior a hora e dia atuais.')


class Submission(models.Model):
    class Results(models.TextChoices):
        # Values must NOT be changed as they are equal to judge service responses
        ACCEPTED = 'ACCEPTED', "Aceito"
        WRONG_ANSWER = 'WRONG_ANSWER', "Resposta Incorreta"
        PRESENTATION_ERROR = 'PRESENTATION_ERROR', "Erro de Apresentação"
        COMPILATION_ERROR = 'COMPILATION_ERROR', "Erro de Compilação"
        RUNTIME_ERROR = 'RUNTIME_ERROR', "Erro de Execução"
        TIME_LIMIT_EXCEEDED = 'TIME_LIMIT_EXCEEDED', "Limite de Tempo Excedido"
        WAITING = 'WAITING', "Aguardando"

    question = models.ForeignKey(Question, verbose_name='Questão', on_delete=RESTRICT, related_name='submissions')
    student = models.ForeignKey(Student, verbose_name='Aluno', on_delete=RESTRICT, related_name='submissions')
    code = models.TextField(verbose_name="Código")
    submitted_at = models.DateTimeField(verbose_name='Submetido em', auto_now_add=True, editable=False)
    judged_at = models.DateTimeField(verbose_name='Julgado em', blank=True, null=True)
    result = models.CharField(verbose_name='Resultado', max_length=30, blank=True, null=True,
                              choices=Results.choices)
    list_schedule = models.ForeignKey(ListSchedule, verbose_name='Agendamento', on_delete=RESTRICT,
                                      related_name='submissions')

    class Meta:
        verbose_name = 'Submissão'
        verbose_name_plural = 'Submissões'

    def __str__(self):
        return '#' + str(self.pk)

    def clean(self):
        if Submission.objects.filter(question=self.question, student=self.student,
                                     list_schedule=self.list_schedule, result=self.Results.ACCEPTED
                                     ).exists():
            raise ValidationError('Já existe uma submissão aceita.')
        elif self.question not in self.list_schedule.question_list.questions.all():
            raise ValidationError('Essa questão não pertence a essa lista.')
        elif self.student.active_class != self.list_schedule.course_class:
            raise ValidationError('Essa lista não é da turma do aluno escolhido.')

