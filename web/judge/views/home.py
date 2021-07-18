from django.db.models import Count
from django.views.generic import TemplateView

from judge import helpers
from judge.helpers import *
from judge.models import CourseClass, ListSchedule, Question


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
            course_class = user.student.active_class
            schedules = course_class.schedules.filter(start_date__lte=timezone.localtime())
            if schedules.count() > 0:
                percentage_sum = 0
                percentage_count = 0
                for schedule in schedules:
                    percentage_sum += helpers.get_student_acceptance_percentage(user.student, schedule)
                    percentage_count += 1
                data['total_percentage'] = percentage_sum/percentage_count
        else:
            schedules = ListSchedule.objects.none()


        submissions = helpers.get_submissions_for_user_and_schedules(user, schedules)
        submissions_results = submissions.order_by().values('result').annotate(count=Count('pk', distinct=True))
        data['result_labels'] = []
        data['result_values'] = []
        data['second_count'] = 0
        for counting_obj in submissions_results:
            if counting_obj['result']:
                data['result_labels'].append(models.Submission.Results(counting_obj['result']).label)
                data['result_values'].append(counting_obj['count'])
                data['second_count'] += counting_obj['count']

        data['first_count'] = schedules.count()
        data['classes_count'] = classes_count

        return data


class HelpView(TemplateView):
    template_name = 'judge/help.html'
