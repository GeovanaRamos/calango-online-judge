from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from judge import helpers
from judge.decorators import professor_required
from judge.forms import ListForm, ScheduleCreateForm, ScheduleUpdateForm
from judge.models import ListSchedule, QuestionList, Submission, CourseClass


class ScheduleListView(ListView):
    model = ListSchedule
    template_name = 'judge/schedule_list.html'

    def get_queryset(self):
        return helpers.get_list_schedules_for_user(self.request.user)


class ScheduleDetailView(DetailView):
    model = ListSchedule
    template_name = 'judge/schedule_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        user = self.request.user

        data['questions'] = helpers.get_schedule_question_info_for_user(self.object, user)
        if hasattr(user, 'student'):
            data['percentage'] = helpers.get_student_acceptance_percentage(user.student, self.object)

        return data


@method_decorator([professor_required], name='dispatch')
class ScheduleClassDetailView(DetailView):
    model = ListSchedule
    template_name = 'judge/schedule_class_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data['questions'] = helpers.get_schedule_question_info_for_user(self.object, self.request.user)
        data['course_class'] = CourseClass.objects.get(pk=self.kwargs['class_pk'])

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
    form_class = ScheduleCreateForm
    template_name = 'judge/schedule_create.html'
    success_url = reverse_lazy('schedule_list')

    def get_form_kwargs(self):
        kwargs = super(ScheduleCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user.professor})
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['course_class'].queryset = form.fields['course_class'].queryset.filter(
            professor=self.request.user.professor)
        return form


@method_decorator([professor_required], name='dispatch')
class ScheduleUpdateView(UpdateView):
    model = ListSchedule
    form_class = ScheduleUpdateForm
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

        data['students'] = helpers.get_students_and_results(self.object)
        data['accepted'] = Submission.ACCEPTED
        data['no_submission'] = Submission.NO_SUBMISSION
        data['unnacepted'] = Submission.UNACCEPTED

        if 'class_pk' in self.kwargs:
            data['course_class'] = CourseClass.objects.get(pk=self.kwargs['class_pk'])

        return data

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if request.GET.get('format', False) == 'csv':
            return helpers.export_csv_file(context['students'], self.object)
        else:
            return self.render_to_response(context)
