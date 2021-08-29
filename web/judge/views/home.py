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
            schedules = helpers.get_list_schedules_for_professor(user.professor)
            classes_count = user.professor.active_classes.count()
            submissions = Submission.objects.filter(list_schedule__in=schedules.all()).distinct()
        elif hasattr(user, 'student') and user.student.active_class:
            schedules = helpers.get_list_schedules_for_student(user.student)
            data['attempts'] = helpers.get_attempts_average_for_student(schedules, user.student)
            data['class_attempts'] = helpers.get_attempts_average_for_class(schedules, user.student.active_class, user)
            data['total_percentage'] = helpers.get_final_percentage_for_student(schedules, user.student)
            submissions = Submission.objects.filter(student=user.student, list_schedule__in=schedules.all()).distinct()
        else:
            submissions = Submission.objects.none()

        data['results'] = helpers.get_submissions_distribution_by_result(submissions)
        data['weekday'] = helpers.get_submissions_distribution_by_day(submissions)
        data['second_count'] = submissions.count()
        data['first_count'] = schedules.count()
        data['classes_count'] = classes_count

        return data


class HelpView(TemplateView):
    template_name = 'judge/help.html'
