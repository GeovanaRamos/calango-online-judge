from django.core.management import BaseCommand
from django.db import transaction
from mixer.backend.django import mixer
from judge import models


class Command(BaseCommand):
    help = 'Populate database'

    @transaction.atomic
    def handle(self, *args, **kwargs):

        admin = models.User.objects.create_superuser('geovana@email.com', 'admin', full_name='geovana ramos')
        models.Student.objects.create(user=admin, registration_number='160122181')

        classes = []
        for i in range(3):
            user = mixer.blend(models.User)
            professor = mixer.blend(models.Professor, user=user)
            classes.append(mixer.blend(models.CourseClass, professor=professor))
            user = mixer.blend(models.User)
            student = mixer.blend(models.Student, user=user)
            student.classes.add(classes[i])

        questions = [mixer.cycle(10).blend(models.Question) for _ in range(3)]

        for i in range(3):
            question_list = mixer.blend(models.QuestionList, questions=questions[i])
            mixer.blend(models.QuestionListApplication, question_list=question_list,
                        course_class=classes[i])

        for _ in range(60):
            mixer.blend(models.TestCase, question=mixer.SELECT)

        for _ in range(30):
            mixer.blend(models.Submission, question=mixer.SELECT, student=mixer.SELECT)

