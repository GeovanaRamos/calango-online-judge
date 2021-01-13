import random

from django.core.management import BaseCommand
from django.db import transaction
from mixer.backend.django import mixer

from accounts.models import User, Student, Professor
from judge import models


class Command(BaseCommand):
    help = 'Populate database'

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
            user = mixer.blend(models.User)
            course_class_1.students.add(mixer.blend(Student, user=user))

        for _ in range(5):
            user = mixer.blend(models.User)
            course_class_2.students.add(mixer.blend(Student, user=user))

        questions = [mixer.cycle(5).blend(models.Question) for _ in range(3)]
        question_lists = [mixer.blend(models.QuestionList, questions=questions[i]) for i in range(3)]
        for i in range(3):
            mixer.blend(models.ListSchedule, question_list=question_lists[i],
                        course_class=random.choice([course_class_1, course_class_2]))

        for _ in range(30):
            mixer.blend(models.TestCase, question=mixer.SELECT)

        for _ in range(30):
            mixer.blend(models.Submission, question=mixer.SELECT, student=mixer.SELECT,
                        result=random.choice(models.Submission.Results.choices)[0])
