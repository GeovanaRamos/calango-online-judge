from django.db import transaction
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView

from judge import helpers
from judge.decorators import professor_required
from judge.forms import QuestionForm, TestCasesFormSet, TestCaseFormSetHelper
from judge.models import Question, ListSchedule


class SubjectsListView(TemplateView):
    template_name = 'judge/subject_list.html'


class QuestionListView(ListView):
    model = Question
    template_name = 'judge/question_list.html'

    def get_context_data(self, **kwargs):
        data = super(QuestionListView, self).get_context_data(**kwargs)
        data['subject_label'] = Question.Subjects(self.kwargs['subject']).label
        return data

    def get_queryset(self):
        if hasattr(self.request.user, 'student'):
            return Question.objects.filter(subject=self.kwargs['subject'], is_evaluative=False)
        else:
            return Question.objects.filter(subject=self.kwargs['subject'])


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'judge/question_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        user = self.request.user
        list_schedule = None

        if 'schedule_pk' in self.kwargs:
            list_schedule = ListSchedule.objects.get(pk=self.kwargs['schedule_pk'])
            data['schedule'] = list_schedule

        if hasattr(user, 'student'):
            data['is_concluded'] = helpers.question_is_concluded(data['object'], list_schedule, user.student)

        return data


@method_decorator([professor_required], name='dispatch')
class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'judge/question_create.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['cases'] = TestCasesFormSet(self.request.POST)
        else:
            data['cases'] = TestCasesFormSet()
            data['helper'] = TestCaseFormSetHelper()
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

    def get_success_url(self):
        return reverse_lazy('question_detail', kwargs={'pk': self.object.pk})


@method_decorator([professor_required], name='dispatch')
class QuestionUpdateView(UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'judge/question_create.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['cases'] = TestCasesFormSet(self.request.POST, instance=self.object)
        else:
            data['cases'] = TestCasesFormSet(instance=self.object)
            data['helper'] = TestCaseFormSetHelper()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        inlines = context['cases']

        self.object = form.save(commit=False)
        self.object.save()

        with transaction.atomic():

            if inlines.is_valid():
                inlines.instance = self.object
                inlines.save()
        return super(QuestionUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('question_detail', kwargs={'pk': self.kwargs['pk']})
