from django.views.generic import ListView
from judge import models


class QuestionListApplicationList(ListView):
    model = models.QuestionListApplication
    template_name = 'judge/question_list_application_list.html'

    def get_queryset(self):
        return models.QuestionListApplication.objects.filter(
            course_class__in=self.request.user.get_classes())

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(QuestionListApplicationList, self).get_context_data(**kwargs)

        if hasattr(self.request.user, 'student'):
            for application in data['object_list']:
                application.concluded = application.student_has_concluded(self.request.user.student)

        return data
