from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from judge import helpers
from judge.models import ListSchedule, Question


def professor_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and hasattr(u, 'professor'),
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def open_question_required(view_func):
    def wrapped(request, *args, **kwargs):
        schedule_pk = kwargs.get('schedule_pk')
        question_pk = kwargs.get('question_pk')
        question = Question.objects.get(pk=question_pk)
        schedule = ListSchedule.objects.get(pk=schedule_pk)

        if helpers.question_is_closed_to_submit(question, schedule, request.user.student) or \
                question not in schedule.question_list.questions.all() or \
                request.user.student.active_class != schedule.course_class:
            kwargs = {'schedule_pk': schedule_pk, 'pk': question_pk}
            return HttpResponseRedirect(reverse_lazy('question_detail', kwargs=kwargs))
        else:
            return view_func(request, *args, **kwargs)

    return wrapped
