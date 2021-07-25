from django.contrib.auth.models import update_last_login
from django.utils import timezone

from judge.models import Enrollment


def update_login_info(sender, **kwargs):
    user = kwargs['user']
    if hasattr(user, 'student') and user.student.active_class:
        enrollment = Enrollment.objects.get(course_class=user.student.active_class, student=user.student)
        if not enrollment.last_login:
            enrollment.first_login = timezone.now()
        enrollment.last_login = timezone.now()
        enrollment.save()
    update_last_login(user, **kwargs)


