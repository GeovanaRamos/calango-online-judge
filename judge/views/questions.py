from django.views.generic import ListView, DetailView

from judge import helpers
from judge.models import Question, ListSchedule


class QuestionListView(ListView):
    model = Question
    template_name = 'judge/question_list.html'

    def get_queryset(self):
        return helpers.get_questions_for_user(self.request.user)


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'judge/question_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        if 'schedule_pk' in self.kwargs and hasattr(self.request.user, 'student'):
            list_schedule = ListSchedule.objects.get(pk=self.kwargs['schedule_pk'])
            data['is_closed'] = helpers.question_is_closed_to_submit(data['object'], list_schedule,
                                                                     self.request.user.student)
            data['schedule_pk'] = self.kwargs['schedule_pk']

        return data
