import json
import requests
import re

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from accounts.models import User, Student
from coj import settings
from judge import models


def submit_to_judge_service(code, question_pk, submission):
    test_cases = models.TestCase.objects.filter(question__pk=question_pk)

    cases = []
    for case in test_cases:
        cases.append(
            {
                "input": re.split('\s*\\n\s*', case.inputs.replace("\r", "")),
                "output": case.output.replace("\r", "")
            }
        )

    data = {
        "code": code,
        "cases": cases,
    }

    r = requests.post(settings.COJ_SERVICE_URL, data=json.dumps(data),
                      headers={'content-type': 'application/json'})

    result_json = r.json()
    submission.result = result_json['message']
    submission.judged_at = timezone.localtime()
    submission.save()

    return result_json['message'] + ': ' + result_json['errorMessage']


def create_or_update_student(students, course_class):
    for student in students:
        user, was_created = User.objects.get_or_create(email=student[0])
        user.full_name = student[1]
        password = User.objects.make_random_password()
        user.set_password(password)
        user.is_active = True
        user.save()

        student, was_created = Student.objects.get_or_create(user=user, registration_number=student[2])
        student.classes.add(course_class)
        student.save()

        subject = 'COJ - Nova turma'
        data = {'full_name': user.full_name, 'password': password, 'class': course_class}
        html_message = render_to_string('registration/welcome_email.html', data)
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email, ]
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)


