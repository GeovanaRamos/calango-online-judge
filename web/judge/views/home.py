from django.db.models import Count, CharField
from django.db.models.functions import ExtractWeekDay
from django.views.generic import TemplateView

from accounts.models import Student
from judge import helpers
from judge.helpers import *
from judge.models import ListSchedule, Submission


class HomeView(TemplateView):
    template_name = 'judge/home.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        user = self.request.user
        classes_count = 0

        if hasattr(user, 'professor') and user.professor.active_classes:
            schedules = helpers.get_list_schedules_for_user(user)
            classes_count = user.professor.active_classes.count()
        elif hasattr(user, 'student') and user.student.active_class:
            schedules = user.student.active_class.schedules.filter(start_date__lte=timezone.localtime())
            data['attempts'] = helpers.get_attempts_average_for_student(schedules, user.student)
            data['class_attempts'] = helpers.get_attempts_average_for_class(schedules, user.student.active_class, user)
            data['total_percentage'] = helpers.get_final_percentage_for_student(schedules, user.student)
        else:
            schedules = ListSchedule.objects.none()

        submissions = helpers.get_submissions_for_user_and_schedules(user, schedules)

        data['results'] = helpers.get_submissions_distribution_by_result(submissions)
        data['weekday'] = helpers.get_submissions_distribution_by_day(submissions)
        data['second_count'] = submissions.count()
        data['first_count'] = schedules.count()
        data['classes_count'] = classes_count

        return data


class HelpView(TemplateView):
    template_name = 'judge/help.html'
