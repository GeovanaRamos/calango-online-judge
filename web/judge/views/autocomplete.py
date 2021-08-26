from dal_select2.views import Select2QuerySetView
from django.db.models import Q
from django.utils.decorators import method_decorator

from judge.decorators import professor_required
from judge.models import QuestionList, Question


@method_decorator([professor_required], name='dispatch')
class QuestionAutocomplete(Select2QuerySetView):
    def get_queryset(self):

        qs = Question.objects.filter(is_evaluative=True)

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