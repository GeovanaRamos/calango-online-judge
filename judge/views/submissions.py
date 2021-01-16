from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from django_q.tasks import async_task

from judge import helpers
from judge.forms import SubmissionForm
from judge.models import Question, ListSchedule, Submission
from judge.tasks import submit_to_judge_service


class SubmissionCreateView(CreateView):
    model = Submission
    template_name = 'judge/submission_create.html'
    form_class = SubmissionForm
    success_url = reverse_lazy('submission_list')

    def form_valid(self, form):
        self.object = form.save()
        async_task(submit_to_judge_service, form.instance.code, self.kwargs['question_pk'], self.object)
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        form.instance.student = self.request.user.student
        form.instance.result = Submission.Results.WAITING
        form.instance.question = Question.objects.get(pk=self.kwargs['question_pk'])
        form.instance.list_schedule = ListSchedule.objects.get(pk=self.kwargs['schedule_pk'])
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class SubmissionListView(ListView):
    model = Submission
    template_name = 'judge/submission_list.html'

    def get_queryset(self):
        return helpers.get_submissions_for_user(self.request.user)


class SubmissionDetailView(DetailView):
    model = Submission
    template_name = 'judge/submission_detail.html'