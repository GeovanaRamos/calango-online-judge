from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.base import TemplateView
from django_q.tasks import async_task

from judge import models, forms, helpers
from judge.tasks import submit_to_judge_service


class HomeView(TemplateView):
    template_name = 'judge/home.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'student'):
            lists = models.ListSchedule.objects.filter(
                course_class__in=helpers.get_user_classes(self.request.user))
            data['count_lists'] = lists.count()
            data['count_concluded'] = sum(
                1 for lt in lists if helpers.student_has_concluded_list_schedule(self.request.user.student, lt))
            data['count_pending'] = data['count_lists'] - data['count_concluded']
            data['count_questions'] = helpers.get_course_class_questions(
                helpers.get_user_classes(self.request.user).first()).count()
            data['count_submissions'] = models.Submission.objects.filter(student=self.request.user.student).count()
            results = models.Submission.objects.values('result').annotate(count=Count('result'))
            data['result_labels'] = []
            data['result_values'] = []
            for counting_obj in results:
                if counting_obj['result']:
                    data['result_labels'].append(models.Submission.Results(counting_obj['result']).label)
                    data['result_values'].append(counting_obj['count'])

            return data


class ScheduleListView(ListView):
    model = models.ListSchedule
    template_name = 'judge/schedule_list.html'

    def get_queryset(self):
        return models.ListSchedule.objects.filter(
            course_class__in=helpers.get_user_classes(self.request.user))

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        if hasattr(self.request.user, 'student'):
            for schedule_list in data['object_list']:
                schedule_list.concluded = schedule_list.student_has_concluded(self.request.user.student)

        return data


class ScheduleDetailView(DetailView):
    model = models.ListSchedule
    template_name = 'judge/schedule_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        if hasattr(self.request.user, 'student'):
            data['object'].concluded = helpers.student_has_concluded_list_schedule(self.request.user.student,
                                                                                   data['object'])
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
