from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from judge import helpers
from judge.decorators import professor_required
from judge.forms import ListForm, ScheduleForm
from judge.models import ListSchedule, QuestionList, Submission


class ScheduleListView(ListView):
    model = ListSchedule
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
    model = ListSchedule
    template_name = 'judge/schedule_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        questions = data['object'].question_list.questions.all()
        # TODO add concluded and course_class

        question_conclusions = []
        for question in questions:
            question.result = helpers.get_question_status_for_user(self.request.user, question, data['object'])
            question_conclusions.append(question)

        data['questions'] = question_conclusions

        return data


@method_decorator([professor_required], name='dispatch')
class ListCreateView(CreateView):
    model = QuestionList
    form_class = ListForm
    template_name = 'judge/list_create.html'
    success_url = reverse_lazy('schedule_list')

    def form_valid(self, form):
        form.instance.author = self.request.user.professor
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


@method_decorator([professor_required], name='dispatch')
class ScheduleCreateView(CreateView):
    model = ListSchedule
    form_class = ScheduleForm
    template_name = 'judge/schedule_create.html'
    success_url = reverse_lazy('schedule_list')


@method_decorator([professor_required], name='dispatch')
class ScheduleUpdateView(UpdateView):
    model = ListSchedule
    form_class = ScheduleForm
    template_name = 'judge/schedule_create.html'

    def get_success_url(self):
        return reverse_lazy('schedule_detail', kwargs={'pk': self.kwargs['pk']})


@method_decorator([professor_required], name='dispatch')
class ScheduleDeleteView(DeleteView):
    model = ListSchedule
    template_name = 'judge/schedule_delete.html'
    success_url = reverse_lazy('schedule_list')


@method_decorator([professor_required], name='dispatch')
class ResultsDetailView(DetailView):
    model = ListSchedule
    template_name = 'judge/results_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        students = []
        for s in data['object'].course_class.students.all():
            s.questions = data['object'].question_list.questions.all()
            count, correct = 0, 0
            for q in s.questions:
                q.result = helpers.get_question_status_for_user(s.user, q, data['object'])
                if q.result == Submission.Results.ACCEPTED.label:
                    correct += 1
                count += 1
            s.percentage = correct / count * 100
            students.append(s)

        data['students'] = students
        return data
