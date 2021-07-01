from django.contrib.auth.models import update_last_login
from django.utils import timezone


def update_login_info(sender, **kwargs):
    user = kwargs['user']
    if hasattr(user, 'student') and not user.last_login:
        user.student.first_login = timezone.now()
        user.student.save()
    update_last_login(user, **kwargs)


