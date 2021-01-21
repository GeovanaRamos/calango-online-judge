from django.db.models import Count
from django.views.generic import TemplateView

from judge import helpers
from judge.helpers import *
from judge.models import CourseClass


class HomeView(TemplateView):
    template_name = 'judge/home.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        user = self.request.user

        if hasattr(user, 'student'):
            course_class = user.student.active_class
        elif 'class_pk' not in self.kwargs:
            course_class = user.professor.active_classes.order_by('-year', '-semester').first()
        else:
            course_class = CourseClass.objects.get(pk=self.kwargs['class_pk'])

        schedules = course_class.schedules.all()
        submissions = helpers.get_submissions_for_user_and_schedules(user, schedules)

        data['first_count'] = schedules.count()

        submissions_results = submissions.order_by().values('result').annotate(count=Count('pk', distinct=True))
        data['result_labels'] = []
        data['result_values'] = []
        data['second_count'] = 0
        for counting_obj in submissions_results:
            if counting_obj['result']:
                data['result_labels'].append(models.Submission.Results(counting_obj['result']).label)
                data['result_values'].append(counting_obj['count'])
                data['second_count'] += counting_obj['count']

        data['course_class'] = course_class

        return data
