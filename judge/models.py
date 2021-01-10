from django.contrib.auth.models import AbstractUser
from django.db import models
from accounts.models import User, Professor, Student


class CourseClass(models.Model):
    name = models.CharField(verbose_name='Nome', max_length=50,
                            choices=[('APC', 'Algoritmos e Programação para Computadores')])
    year = models.PositiveSmallIntegerField(verbose_name='Ano')
    semester = models.PositiveSmallIntegerField(verbose_name='Semestre', choices=[(1, 1), (2, 2)])
    professor = models.ForeignKey(Professor, verbose_name='Professor', on_delete=models.RESTRICT,
                                  related_name='classes')
    is_active = models.BooleanField(verbose_name='Ativa?', default=True)

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'

    def __str__(self):
        return self.name + ' - ' + str(self.year) + '/' + str(self.semester)


class Question(models.Model):
    class Subjects(models.TextChoices):
        SEQ = 'SEQ', "Estruturas Sequenciais e Condicionais"
        MOD = 'MOD', "Modularização"
        COND = 'COND', "Estruturas Condionais e de Repetição"
        VET = 'VET', "Vetores"

    name = models.CharField(verbose_name='Nome', max_length=35)
    description = models.TextField(verbose_name='Enunciado')
    subject = models.CharField(verbose_name='Assunto', choices=Subjects.choices, max_length=40)

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'

    def __str__(self):
        return self.name


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


class QuestionList(models.Model):
    name = models.CharField(verbose_name='Nome', max_length=50)
    questions = models.ManyToManyField(Question, verbose_name='Questões', related_name='lists')

    class Meta:
        verbose_name = 'Lista de Exercícios'
        verbose_name_plural = 'Listas de Exercicíos'

    def __str__(self):
        return self.name


class ListSchedule(models.Model):
    name = models.CharField(verbose_name='Nome', max_length=40)
    start_date = models.DateTimeField(verbose_name="Data de Início", auto_now=False, auto_now_add=False)
    due_date = models.DateTimeField(verbose_name="Data de Término", auto_now=False, auto_now_add=False)
    course_class = models.ForeignKey(CourseClass, verbose_name='Turma', on_delete=models.RESTRICT,
                                     related_name='schedules')
    question_list = models.ForeignKey(QuestionList, verbose_name='Lista de Exercícios',
                                      on_delete=models.RESTRICT, related_name='schedules')

    class Meta:
        verbose_name = 'Agendamento de Lista'
        verbose_name_plural = 'Agendamentos de Listas'


class Submission(models.Model):
    class Results(models.TextChoices):
        ACCEPTED = 'ACCEPTED', "Aceito"
        WRONG_ANSWER = 'WRONG_ANSWER', "Resposta Incorreta"
        PRESENTATION_ERROR = 'PRESENTATION_ERROR', "Erro de Apresentação"
        COMPILATION_ERROR = 'COMPILATION_ERROR', "Erro de Compilação"
        RUNTIME_ERROR = 'RUNTIME_ERROR', "Erro de Execução"
        TIME_LIMIT_EXCEEDED = 'TIME_LIMIT_EXCEEDED', "Limite de Tempo Excedido"
        WAITING = 'WAITING', "Aguardando"

    question = models.ForeignKey(Question, verbose_name='Questão', on_delete=models.RESTRICT,
                                 related_name='submissions')
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
