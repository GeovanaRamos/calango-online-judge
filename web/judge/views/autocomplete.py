from dal_select2.views import Select2QuerySetView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from judge import helpers
from judge.decorators import professor_required
from judge.forms import ListForm, ScheduleCreateForm, ScheduleUpdateForm
from judge.models import ListSchedule, QuestionList, Submission, CourseClass, Question


@method_decorator([professor_required], name='dispatch')
class QuestionAutocomplete(Select2QuerySetView):
    def get_queryset(self):

        qs = Question.objects.all()

        if self.q:
            qs = qs.filter(Q(name__istartswith=self.q) | Q(subject__istartswith=self.q))

        return qs


@method_decorator([professor_required], name='dispatch')
class ListAutocomplete(Select2QuerySetView):
    def get_queryset(self):

        qs = QuestionList.objects.filter(author=self.request.user.professor)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs