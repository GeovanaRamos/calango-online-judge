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
    identifier = models.CharField(verbose_name='Identificador da Turma', max_length=5)

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'

    def __str__(self):
        return self.discipline + ' - ' + str(self.year) + '/' + str(self.semester) + ' - Turma ' + self.identifier

    def save(self, *args, **kwargs):
        if not self.is_active:
            for student in self.students.all():
                student.user.is_active = False
                student.user.save()
        super(CourseClass, self).save()


class Question(models.Model):
    class Subjects(models.TextChoices):
        SEQUENCES = 'SEQUENCES', "Estruturas Sequenciais"
        CONDITIONS = 'CONDITIONS', "Estruturas Condicionais"
        REPETITIONS = 'REPETITIONS', "Estruturas de Repetição"
        MODULARIZATION = 'MODULARIZATION', "Modularização"
        VECTORS = 'VECTORS', "Vetores"

    name = models.CharField(verbose_name='Nome', max_length=35)
    description = models.TextField(verbose_name='Enunciado')
    subject = models.CharField(verbose_name='Assunto', choices=Subjects.choices, max_length=15)
    author = models.ForeignKey(Professor, verbose_name='Autor', on_delete=RESTRICT, related_name='questions')
    is_evaluative = models.BooleanField(verbose_name='Avaliativa?', default=True)

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'

    def __str__(self):
        return self.name + " - " + self.get_subject_display()


class TestCase(models.Model):
    inputs = models.TextField(verbose_name='Entradas')
    output = models.TextField(verbose_name='Saída')
    question = models.ForeignKey(Question, verbose_name='Questão', on_delete=CASCADE, related_name='cases')
    is_hidden = models.BooleanField(verbose_name='Ocultar?', default=False)

    class Meta:
        verbose_name = 'Caso de Teste'
        verbose_name_plural = 'Casos de Teste'

    def __str__(self):
        return self.question.name + ' - Caso: ' + str(self.pk)


class QuestionList(models.Model):
    name = models.CharField(verbose_name='Nome da Lista', max_length=50)
    questions = models.ManyToManyField(Question, verbose_name='Questões', related_name='lists')
    author = models.ForeignKey(Professor, verbose_name='Autor', on_delete=RESTRICT, related_name='lists')

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

    @property
    def is_closed(self):
        return self.due_date < timezone.now() or timezone.localtime() < self.start_date

    def __str__(self):
        return self.question_list.name + ' - ' + self.course_class.__str__()

    def clean(self):
        if self.due_date < self.start_date:
            raise ValidationError('A data de término deve ser posterior a de início.')


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
                                      related_name='submissions', blank=True, null=True)
    course_class = models.ForeignKey(CourseClass, verbose_name='Turma', on_delete=RESTRICT, related_name='submissions',
                                     blank=True, null=True)

    class Meta:
        verbose_name = 'Submissão'
        verbose_name_plural = 'Submissões'

    def __str__(self):
        return '#' + str(self.pk)

    def clean(self):
        """
            If the question is_evaluative, it will be linked to a list_schedule, otherwise it will be linked
            to a course_class. This way, students can conclude the same questions if they fail the course
            and retake it in another semester/class. Restrictions:

            1. Can't have course_class + list_schedule
            2. If it is NOT evaluative, check if student is in course_class
            3. If it is NOT evaluative, check if there is an accepted submission for course_class
            4. If it is evaluative, check if question is in list_schedule's question_list
            5. If it is evaluative, check if student is in list_schedule's course_class
            6. If it is evaluative, check if there is an accepted submission for list_schedule
        """

        if self.list_schedule and self.course_class:
            raise ValidationError('A submissão deve ser avulsa ou avaliativa. Escolha uma lista OU uma turma.')

        elif self.list_schedule:  # is evaluative

            if not self.question.is_evaluative:
                raise ValidationError('Esta questão não é avaliativa e não pode ser vinculada a uma lista.')
            elif self.question not in self.list_schedule.question_list.questions.all():
                raise ValidationError('Esta questão não pertence a esta lista.')
            elif not self.list_schedule.course_class.students.filter(
                    registration_number=self.student.registration_number).exists():
                raise ValidationError('Esta lista não é da turma do aluno escolhido.')
            elif Submission.objects.filter(question=self.question, student=self.student,
                                           list_schedule=self.list_schedule, result=self.Results.ACCEPTED).exists():
                submission = Submission.objects.get(question=self.question, student=self.student,
                                                    list_schedule=self.list_schedule, result=self.Results.ACCEPTED)
                if self != submission:  # because queryset contains self object
                    raise ValidationError('Já existe uma submissão aceita.')

        elif self.course_class:  # is detached/single question

            if self.question.is_evaluative:
                raise ValidationError('Esta questão é avaliativa e deve ser vinculada a uma lista.')
            elif not self.course_class.students.filter(registration_number=self.student.registration_number).exists():
                raise ValidationError('Esta turma não é a do aluno escolhido.')
            elif Submission.objects.filter(question=self.question, student=self.student,
                                           course_class=self.course_class, result=self.Results.ACCEPTED).exists():
                submission = Submission.objects.get(question=self.question, student=self.student,
                                                    course_class=self.course_class, result=self.Results.ACCEPTED)
                if self != submission:  # because queryset contains self object
                    raise ValidationError('Já existe uma submissão aceita.')

        else:  # is neither evaluative or detached
            raise ValidationError('A submissão deve ser avulsa ou avaliativa. Escolha uma lista OU uma turma.')
