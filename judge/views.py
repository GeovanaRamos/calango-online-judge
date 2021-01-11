from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django_q.tasks import async_task

from judge import models, forms, helpers
from judge.tasks import submit_to_judge_service


class HomeView(TemplateView):
    template_name = 'judge/home.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        user = self.request.user
        lists = helpers.get_list_schedules_for_user(user)

        # BOX
        data['count_lists'] = lists.count()
        data['count_questions'] = helpers.get_questions_for_list_schedules(lists)

        # CHART
        data['count_concluded'] = helpers.get_list_schedule_conclusions(lists, user)
        data['count_pending'] = data['count_lists'] - data['count_concluded'] # TODO professor

        submissions_results = helpers.get_submissions_results_for_user(user)
        data['result_labels'] = []
        data['result_values'] = []
        data['count_submissions'] = 0
        for counting_obj in submissions_results:
            if counting_obj['result']:
                data['result_labels'].append(models.Submission.Results(counting_obj['result']).label)
                data['result_values'].append(counting_obj['count'])
                data['count_submissions'] += counting_obj['count']

        return data


class ScheduleListView(ListView):
    model = models.ListSchedule
    template_name = 'judge/schedule_list.html'

    def get_queryset(self):
        return helpers.get_list_schedules_for_user(self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        user = self.request.user

        if hasattr(user, 'student'):
            for ls in data['object_list']:
                ls.concluded = helpers.student_has_concluded_list_schedule(user.student, ls)

        return data


class ScheduleDetailView(DetailView):
    model = models.ListSchedule
    template_name = 'judge/schedule_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        questions = data['object'].question_list.questions.all()
        #TODO add concluded and course_class

        question_conclusions = []
        for question in questions:
            question.result = helpers.get_question_status_for_user(self.request.user, question)
            question_conclusions.append(question)

        data['questions'] = question_conclusions

        return data


class QuestionDetailView(DetailView):
    model = models.Question
    template_name = 'judge/question_detail.html'


class SubmissionCreateView(CreateView):
    model = models.Submission
    template_name = 'judge/submission_create.html'
    form_class = forms.SubmissionForm
    success_url = reverse_lazy('submission_list')

    def form_valid(self, form):
        form.instance.question = models.Question.objects.get(pk=self.kwargs['question_pk'])
        form.instance.student = self.request.user.student
        form.instance.result = models.Submission.Results.WAITING
        self.object = form.save()
        async_task(submit_to_judge_service, form.instance.code, self.kwargs['question_pk'], self.object)
        return HttpResponseRedirect(self.get_success_url())


class SubmissionListView(ListView):
    model = models.Submission
    template_name = 'judge/submission_list.html'

    def get_queryset(self):
        return helpers.get_submissions_for_user(self.request.user)


class SubmissionDetailView(DetailView):
    model = models.Submission
    template_name = 'judge/submission_detail.html'


class ClassListView(ListView):
    model = models.CourseClass
    template_name = 'judge/class_list.html'


class QuestionListView(ListView):
    model = models.Question
    template_name = 'judge/question_list.html'

    def get_queryset(self):
        return helpers.get_questions_for_user(self.request.user)


class ListCreateView(CreateView):
    model = models.QuestionList
    form_class = forms.ListForm
    template_name = 'judge/list_create.html'
    success_url = reverse_lazy('schedule_list')


class ScheduleCreateView(CreateView):
    model = models.ListSchedule
    form_class = forms.ScheduleForm
    template_name = 'judge/schedule_create.html'
    success_url = reverse_lazy('schedule_list')


class ScheduleUpdateView(UpdateView):
    model = models.ListSchedule
    form_class = forms.ScheduleForm
    template_name = 'judge/schedule_create.html'

    def get_success_url(self):
        return reverse('schedule_detail', kwargs={'pk': self.kwargs['pk']})


class ScheduleDeleteView(DeleteView):
    model = models.ListSchedule
    template_name = 'judge/schedule_delete.html'
    success_url = reverse_lazy('schedule_list')


class ResultsDetailView(DetailView):
    model = models.ListSchedule
    template_name = 'judge/results_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        students = []
        for s in data['object'].course_class.students.all():
            s.questions = data['object'].question_list.questions.all()
            count, correct = 0, 0
            for q in s.questions:
                q.result = helpers.get_question_status_for_user(s.user, q)
                if q.result == models.Submission.Results.ACCEPTED.label:
                    correct += 1
                count += 1
            s.percentage = correct/count * 100
            students.append(s)

        data['students'] = students
        return data
