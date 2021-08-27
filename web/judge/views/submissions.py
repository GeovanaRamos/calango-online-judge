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
from judge.models import Question, ListSchedule, Submission
from judge.tasks import submit_to_judge_service


@method_decorator([open_question_required], name='dispatch')
class SubmissionCreateView(CreateView):
    model = Submission
    template_name = 'judge/submission_create.html'
    form_class = SubmissionForm
    success_url = reverse_lazy('submission_list')

    def dispatch(self, request, *args, **kwargs):
        self.question = Question.objects.get(pk=kwargs['question_pk'])
        self.course_class = self.request.user.student.active_class
        if 'schedule_pk' in kwargs:
            self.list_schedule = ListSchedule.objects.get(pk=kwargs['schedule_pk'])
        return super(SubmissionCreateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SubmissionCreateView, self).get_form_kwargs()
        kwargs.update({'course_class':  self.course_class})
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(SubmissionCreateView, self).get_context_data(**kwargs)
        if 'schedule_pk' in self.kwargs:
            data['schedule'] = self.list_schedule
        data['question'] = self.question
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

        if hasattr(self, 'list_schedule'):
            form.instance.list_schedule = self.list_schedule
        else:
            form.instance.course_class = self.course_class

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class SubmissionListView(ListView):
    model = Submission
    template_name = 'judge/submission_list.html'

    def get_queryset(self):
        if hasattr(self.request.user, 'professor'):
            data = self.request.GET
            id = data.get('id')
            student_name = data.get('student_name')
            student_number = data.get('student_number')
            question_id = data.get('question_id')
            question_name = data.get('question_name')
            return helpers.search_submissions(self.request.user, id, student_name, student_number, question_id,
                                              question_name)
        else:
            return helpers.get_all_active_submissions_for_student(self.request.user.student)


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
