import csv

from django.http import HttpResponseRedirect, HttpResponse
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
        return data


class ScheduleDetailView(DetailView):
    model = ListSchedule
    template_name = 'judge/schedule_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        user = self.request.user
        questions = self.object.question_list.questions.order_by('pk').all()

        question_conclusions = []
        for question in questions:
            question.result = helpers.get_question_status_for_user(user, question, data['object'])
            question_conclusions.append(question)

        data['questions'] = question_conclusions

        if hasattr(user, 'student'):
            data['percentage'] = helpers.get_student_acceptance_percentage(user.student, self.object)

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

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['course_class'].queryset = form.fields['course_class'].queryset.filter(
            professor=self.request.user.professor)
        return form


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
        data['accepted_label'] = Submission.Results.ACCEPTED.label
        data['no_submission_label'] = Submission.NO_SUBMISSION
        return data

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if request.GET.get('format', False) == 'csv':
            return export_csv_file(request, context['students'], self.object)
        else:
            return self.render_to_response(context)


def export_csv_file(request, students, list_schedule):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=' + list_schedule.__str__() + '.csv'

    writer = csv.writer(response)

    for student in students:
        writer.writerow([student.registration_number, student.user.full_name, student.percentage])

    return response
