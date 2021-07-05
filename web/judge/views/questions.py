from django.db import transaction
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, TemplateView

from judge import helpers
from judge.decorators import professor_required
from judge.forms import QuestionForm, TestCasesFormSet
from judge.models import Question, ListSchedule


@method_decorator([professor_required], name='dispatch')
class SubjectsListView(TemplateView):
    template_name = 'judge/subject_list.html'


@method_decorator([professor_required], name='dispatch')
class QuestionListView(ListView):
    model = Question
    template_name = 'judge/question_list.html'

    def get_context_data(self, **kwargs):
        data = super(QuestionListView, self).get_context_data(**kwargs)
        data['subject_label'] = Question.Subjects(self.kwargs['subject']).label
        return data

    def get_queryset(self):
        return Question.objects.filter(subject=self.kwargs['subject'])


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'judge/question_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        if 'schedule_pk' in self.kwargs:
            data['schedule_pk'] = self.kwargs['schedule_pk']
            list_schedule = ListSchedule.objects.get(pk=self.kwargs['schedule_pk'])
            data['schedule_name'] = list_schedule.question_list.name
            if hasattr(self.request.user, 'student'):
                data['is_closed'] = helpers.question_is_closed_to_submit(data['object'], list_schedule,
                                                                         self.request.user.student)

        return data


@method_decorator([professor_required], name='dispatch')
class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'judge/question_create.html'
    success_url = reverse_lazy('subject_list')

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
