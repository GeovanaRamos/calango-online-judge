from django.http import HttpResponseRedirect, JsonResponse

from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View

from django.views.generic import CreateView, FormView, ListView, DeleteView, TemplateView, UpdateView
from django_q.tasks import async_task

from accounts.models import Student
from judge import helpers

from judge.decorators import professor_required
from judge.forms import ClassForm, StudentForm
from judge.models import CourseClass, Enrollment, ListSchedule, Submission
from judge.tasks import create_or_update_student


@method_decorator([professor_required], name='dispatch')
class ClassListView(ListView):
    model = CourseClass
    template_name = 'judge/class_list.html'

    def get_queryset(self):
        return self.request.user.professor.classes.filter(is_active=True)


@method_decorator([professor_required], name='dispatch')
class ClassInactiveListView(ListView):
    model = CourseClass
    template_name = 'judge/class_inactive_list.html'

    def get_queryset(self):
        return self.request.user.professor.classes.filter(is_active=False)


@method_decorator([professor_required], name='dispatch')
class ClassCreateView(CreateView):
    model = CourseClass
    template_name = 'judge/class_create.html'
    form_class = ClassForm
    success_url = reverse_lazy('class_list')

    def form_valid(self, form):
        form.instance.professor = self.request.user.professor
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


@method_decorator([professor_required], name='dispatch')
class ClassUpdateView(UpdateView):
    model = CourseClass
    template_name = 'judge/class_create.html'
    form_class = ClassForm
    success_url = reverse_lazy('class_list')


@method_decorator([professor_required], name='dispatch')
class StudentFormView(FormView):
    form_class = StudentForm
    template_name = 'judge/student_form.html'
    success_url = reverse_lazy('class_list')

    def dispatch(self, request, *args, **kwargs):
        self.course_class = CourseClass.objects.get(pk=self.kwargs['class_pk'])
        return super(StudentFormView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(StudentFormView, self).get_context_data(**kwargs)
        data['course_class'] = self.course_class
        return data

    def form_valid(self, form):
        async_task(create_or_update_student, form.cleaned_data['students'], self.course_class)
        return HttpResponseRedirect(self.get_success_url())


@method_decorator([professor_required], name='dispatch')
class StudentListView(ListView):
    model = Student
    template_name = 'judge/student_list.html'

    def get_queryset(self):
        self.course_class = CourseClass.objects.get(pk=self.kwargs['class_pk'])
        students = self.course_class.students.all().order_by('registration_number')
        for student in students:
            enrollment = Enrollment.objects.get(course_class=self.course_class, student=student)
            student.first_login = enrollment.first_login
            student.last_login = enrollment.last_login

        return students

    def get_context_data(self, **kwargs):
        data = super(StudentListView, self).get_context_data(**kwargs)
        data['course_class'] = self.course_class
        return data


@method_decorator([professor_required], name='dispatch')
class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'judge/student_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        course_class = CourseClass.objects.get(pk=self.kwargs['class_pk'])
        # instead of deleting we just remove from class
        if course_class == self.object.active_class:
            self.object.is_active = False
        course_class.students.remove(self.object)
        course_class.save()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('student_list', kwargs={'class_pk': self.kwargs['class_pk']})


@method_decorator([professor_required], name='dispatch')
class ClassDeleteView(DeleteView):
    model = CourseClass
    template_name = 'judge/class_delete.html'
    success_url = reverse_lazy('class_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # instead of deleting we just deactivate it
        self.object.is_active = False
        # remove student access to the platform
        for student in self.object.students.all():
            student.user.is_active = False
            student.user.save()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


@method_decorator([professor_required], name='dispatch')
class ActivitiesView(TemplateView):
    template_name = 'judge/class_activities.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['course_class'] = CourseClass.objects.get(pk=self.kwargs['class_pk'])
        data['schedules'] = ListSchedule.objects.filter(course_class=data['course_class'])
        data['students'] = []
        for student in data['course_class'].students.all():
            submissions = Submission.objects.filter(course_class=data['course_class'], student=student)
            student.attempts = submissions.count()
            student.concluded = submissions.filter(result=Submission.Results.ACCEPTED).count()
            data['students'].append(student)
        return data

    def get(self, request, *args, **kwargs):
        if request.GET.get('format', False) == 'csv':
            return helpers.export_csv_file_for_all_class_lists(self.kwargs['class_pk'])
        else:
            return super(ActivitiesView, self).get(request, *args, **kwargs)


@method_decorator([professor_required], name='dispatch')
class StudentQuestionsResults(View):

    def post(self, request):
        student_pk = request.POST.get('student_pk')
        class_pk = request.POST.get('class_pk')
        print(student_pk, class_pk)
        course_class = CourseClass.objects.get(pk=class_pk)
        student = Student.objects.get(pk=student_pk)
        questions = Submission.objects.filter(question__is_evaluative=False, student=student,
                                                  course_class=course_class, result=Submission.Results.ACCEPTED).values(
            'question', 'question__name').distinct()
        print(questions)

        return JsonResponse(data={"questions": list(questions)})
