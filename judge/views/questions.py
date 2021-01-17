from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

from judge import helpers
from judge.forms import QuestionForm, TestCasesFormSet
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


class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'judge/question_create.html'
    success_url = reverse_lazy('question_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['cases'] = TestCasesFormSet(self.request.POST)
        else:
            data['cases'] = TestCasesFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        inlines = context['cases']

        self.object = form.save(commit=False)
        self.object.author = self.request.user.professor
        self.object.save()

        with transaction.atomic():

            if inlines.is_valid():
                inlines.instance = self.object
                inlines.save()
        return super(QuestionCreateView, self).form_valid(form)
