from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DetailView
from django_q.tasks import async_task

from accounts.models import Student
from judge import helpers
from judge.decorators import open_question_required
from judge.forms import SubmissionForm
from judge.models import Question, ListSchedule, Submission
from judge.tasks import submit_to_judge_service


@method_decorator([open_question_required], name='dispatch')
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
        user = self.request.user
        if 'schedule_pk' in self.kwargs and hasattr(user, 'professor'):
            student = Student.objects.get(pk=self.kwargs['student_pk'])
            schedule = ListSchedule.objects.get(pk=self.kwargs['schedule_pk'])
            return Submission.objects.filter(student=student, list_schedule=schedule)
        else:
            schedules = user.student.active_class.schedules if user.student.active_class else ListSchedule.objects.none()
            return helpers.get_submissions_for_user_and_schedules(user, schedules).order_by('-submitted_at')


class SubmissionDetailView(DetailView):
    model = Submission
    template_name = 'judge/submission_detail.html'
