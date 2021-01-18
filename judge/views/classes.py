from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, FormView, ListView, DeleteView

from accounts.models import User, Student
from judge import helpers
from judge.decorators import professor_required
from judge.forms import ClassForm, StudentForm
from judge.models import CourseClass


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
        for s in form.cleaned_data['students']:
            print(s)
            user, was_created = User.objects.get_or_create(
                email=s[0],
                full_name=s[1],
            )
            user.set_password(str(s[2]) + s[1].split()[-1])
            user.is_active = True
            user.save()

            student, was_created = Student.objects.get_or_create(
                user=user,
                registration_number=s[2],
            )
            student.classes.add(CourseClass.objects.get(pk=self.kwargs['class_pk']))
            student.save()

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


class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'judge/student_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        course_class = CourseClass.objects.get(pk=self.kwargs['class_pk'])
        # instead of deleting we just remove from class
        course_class.students.remove(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('student_list', kwargs={'class_pk': self.kwargs['class_pk']})


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
