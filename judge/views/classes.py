from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, CreateView, FormView, ListView

from accounts.models import User, Student
from judge import helpers
from judge.decorators import professor_required
from judge.forms import ClassForm, StudentForm
from judge.models import CourseClass, ListSchedule, Submission


@method_decorator([professor_required], name='dispatch')
class ClassListView(ListView):
    model = CourseClass
    template_name = 'judge/class_list.html'


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
        course_class = CourseClass.objects.get(pk=self.kwargs['class_pk'])
        return course_class.students.all()
