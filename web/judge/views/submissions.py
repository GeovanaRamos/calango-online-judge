import json

import requests
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, ListView, DetailView
from django_q.tasks import async_task

from accounts.models import Student
from coj import settings
from judge import helpers
from judge.decorators import open_question_required, submission_author_or_professor_required, professor_required
from judge.forms import SubmissionForm
from judge.helpers import get_judge_post_data
from judge.models import Question, ListSchedule, Submission, TestCase
from judge.tasks import submit_to_judge_service


@method_decorator([open_question_required], name='dispatch')
class SubmissionCreateView(CreateView):
    model = Submission
    template_name = 'judge/submission_create.html'
    form_class = SubmissionForm
    success_url = reverse_lazy('submission_list')
    
    def dispatch(self, request, *args, **kwargs):
        self.question = Question.objects.get(pk=kwargs['question_pk'])
        self.list_schedule = ListSchedule.objects.get(pk=kwargs['schedule_pk'])
        return super(SubmissionCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(SubmissionCreateView, self).get_context_data(**kwargs)
        data['schedule_pk'] = self.list_schedule.pk
        data['schedule_name'] = self.list_schedule.question_list.name
        data['question_name'] = self.question.name
        data['question_pk'] = self.question.pk
        return data

    def form_valid(self, form):
        self.object = form.save()
        async_task(submit_to_judge_service, form.instance.code, self.kwargs['question_pk'], self.object)
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        form.instance.student = self.request.user.student
        form.instance.result = Submission.Results.WAITING
        form.instance.question = self.question
        form.instance.list_schedule = self.list_schedule
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
            self.student = Student.objects.get(pk=self.kwargs['student_pk'])
            self.schedule = ListSchedule.objects.get(pk=self.kwargs['schedule_pk'])
            return Submission.objects.filter(student=self.student, list_schedule=self.schedule).order_by(
                '-submitted_at')
        else:
            schedules = user.student.active_class.schedules if user.student.active_class else ListSchedule.objects.none()
            return helpers.get_submissions_for_user_and_schedules(user, schedules).order_by('-submitted_at')

    def get_context_data(self, **kwargs):
        data = super(SubmissionListView, self).get_context_data(**kwargs)
        if 'student_pk' in self.kwargs and hasattr(self.request.user, 'professor'):
            data['student'] = self.student
            data['schedule'] = self.schedule
        return data


@method_decorator([submission_author_or_professor_required], name='dispatch')
class SubmissionDetailView(DetailView):
    model = Submission
    template_name = 'judge/submission_detail.html'


@method_decorator([professor_required], name='dispatch')
class SubmissionTest(View):

    def post(self, request):
        code = request.POST.get('code')
        question_pk = request.POST.get('question_pk')

        data = get_judge_post_data(code, question_pk)

        r = requests.post(settings.COJ_SERVICE_URL, data=json.dumps(data),
                          headers={'content-type': 'application/json'})
        result_json = r.json()
        result = result_json['message']
        error_message = result_json['errorMessage']

        return JsonResponse(data={"result": result, "error_message": error_message})

