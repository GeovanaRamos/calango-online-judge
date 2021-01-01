from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from django_q.tasks import async_task

from judge import models, forms
from judge.utils import submit_to_judge_service


class ScheduleListView(ListView):
    model = models.ListSchedule
    template_name = 'judge/schedule_list.html'

    def get_queryset(self):
        return models.ListSchedule.objects.filter(
            course_class__in=self.request.user.get_classes())

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)

        if hasattr(self.request.user, 'student'):
            for schedule_list in data['object_list']:
                schedule_list.concluded = schedule_list.student_has_concluded(self.request.user.student)

        return data


class ScheduleDetailView(DetailView):
    model = models.ListSchedule
    template_name = 'judge/schedule_detail.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)

        if hasattr(self.request.user, 'student'):
            data['object'].concluded = data['object'].student_has_concluded(self.request.user.student)
            questions = []
            for question in data['object'].question_list.questions.all():
                question.result = question.get_status_for_student(self.request.user.student)
                questions.append(question)

            data['questions'] = questions

        return data


class QuestionDetailView(DetailView):
    model = models.Question
    template_name = 'judge/question_detail.html'


class SubmissionCreateView(CreateView):
    model = models.Submission
    template_name = 'judge/submission_create.html'
    form_class = forms.SubmissionForm

    def form_valid(self, form):
        form.instance.question = models.Question.objects.get(pk=self.kwargs['question_pk'])
        form.instance.student = self.request.user.student
        form.instance.result = models.Submission.Results.WAITING
        self.object = form.save()
        async_task(submit_to_judge_service, form.instance.code, self.kwargs['question_pk'], self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('question_detail', kwargs={'pk': self.kwargs['question_pk']})


class SubmissionListView(ListView):
    model = models.Submission
    template_name = 'judge/submission_list.html'

    def get_queryset(self):
        return models.Submission.objects.filter(student=self.request.user.student).order_by('-submitted_at')


class SubmissionDetailView(DetailView):
    model = models.Submission
    template_name = 'judge/submission_detail.html'


