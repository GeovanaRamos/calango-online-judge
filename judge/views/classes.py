from itertools import repeat
from multiprocessing import Pool


from django.http import HttpResponseRedirect

from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from django.views.generic import CreateView, FormView, ListView, DeleteView
from django_q.tasks import async_task

from accounts.models import Student

from judge.decorators import professor_required
from judge.forms import ClassForm, StudentForm
from judge.models import CourseClass
from judge.tasks import create_or_update_student


@method_decorator([professor_required], name='dispatch')
class ClassListView(ListView):
    model = CourseClass
    template_name = 'judge/class_list.html'


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
class StudentFormView(FormView):
    form_class = StudentForm
    template_name = 'judge/student_form.html'
    success_url = reverse_lazy('class_list')

    def form_valid(self, form):
        course_class = CourseClass.objects.get(pk=self.kwargs['class_pk'])
        async_task(create_or_update_student, form.cleaned_data['students'], course_class)
        return HttpResponseRedirect(self.get_success_url())


@method_decorator([professor_required], name='dispatch')
class StudentListView(ListView):
    model = Student
    template_name = 'judge/student_list.html'

    def get_queryset(self):
        self.course_class = CourseClass.objects.get(pk=self.kwargs['class_pk'])
        return self.course_class.students.all()

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
