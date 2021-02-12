import random

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone
from mixer.backend.django import mixer

from accounts.models import User, Student, Professor
from judge import models


class Command(BaseCommand):
    help = 'Populate database'

    def create_submission(self, question, students, result, schedule):
        mixer.blend(models.Submission, question=question, student=random.choice(students),
                    result=result, list_schedule=schedule, judged_at=timezone.localtime())

    @transaction.atomic
    def handle(self, *args, **kwargs):

        user_student = User.objects.create_superuser('aluno@email.com', 'admin', full_name='Joao Pedro Ramos')
        student = Student.objects.create(user=user_student, registration_number=160122181)
        user_professor = User.objects.create_superuser('professor@email.com', 'admin',
                                                       full_name='Marilia Pereira Silva')
        professor = Professor.objects.create(user=user_professor)

        course_class_1 = mixer.blend(models.CourseClass, professor=professor)
        course_class_1.students.add(student)
        course_class_2 = mixer.blend(models.CourseClass, professor=professor)

        for _ in range(5):
            course_class_1.students.add(mixer.blend(Student, user=mixer.blend(models.User)))
            course_class_2.students.add(mixer.blend(Student, user=mixer.blend(models.User)))

        questions = [mixer.cycle(5).blend(models.Question) for _ in range(3)]
        question_lists = [mixer.blend(models.QuestionList, questions=questions[i]) for i in range(3)]
        for i in range(3):
            mixer.blend(models.ListSchedule, question_list=question_lists[i],
                        course_class=random.choice([course_class_1, course_class_2]))

        for schedule in models.ListSchedule.objects.all():
            students = Student.objects.all()
            for question in schedule.question_list.questions.all():

                for _ in range(4):
                    mixer.blend(models.TestCase, question=question)

                # accepted must be the last one
                for _ in range(5):
                    self.create_submission(question, students, models.Submission.Results.COMPILATION_ERROR, schedule)
                    self.create_submission(question, students, models.Submission.Results.RUNTIME_ERROR, schedule)
                    self.create_submission(question, students, models.Submission.Results.WRONG_ANSWER, schedule)
                    self.create_submission(question, students, models.Submission.Results.PRESENTATION_ERROR, schedule)
                self.create_submission(question, students, models.Submission.Results.ACCEPTED, schedule)