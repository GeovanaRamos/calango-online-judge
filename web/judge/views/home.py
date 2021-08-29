from django.db.models import Count, CharField
from django.db.models.functions import ExtractWeekDay
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from accounts.models import Student
from judge import helpers
from judge.decorators import professor_required
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


@method_decorator([professor_required], name='dispatch')
class StatisticsView(TemplateView):
    template_name = 'judge/class_statistics.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        course_class = models.CourseClass.objects.get(pk=self.kwargs['class_pk'])
        schedules = models.ListSchedule.objects.filter(course_class=course_class)
        submissions = Submission.objects.filter(list_schedule__in=schedules.all()).distinct()

        data['course_class'] = course_class
        data['schedules_count'] = schedules.count()
        data['submissions_count'] = submissions.count()
        data['attempts'] = helpers.get_attempts_average_for_class(schedules, course_class, None)
        data['concluded_all'] = helpers.get_students_that_concluded_all_questions(schedules, course_class)
        data['not_give_up'] = helpers.get_students_that_did_not_give_up(schedules, course_class)
        data['less_than_75'] = helpers.get_students_that_concluded_less_than_75(schedules, course_class)
        data['tried_non_evaluative'] = helpers.get_students_that_tried_non_evaluative(course_class)
        data['concluded_non_evaluative'] = helpers.get_students_that_concluded_non_evaluative(course_class)

        data['results'] = helpers.get_submissions_distribution_by_result(submissions)
        data['weekday'] = helpers.get_submissions_distribution_by_day(submissions)

        return data
