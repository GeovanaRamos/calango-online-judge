from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from judge import helpers
from judge.models import ListSchedule, Question, Submission


def professor_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and hasattr(u, 'professor'),
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def open_question_required(view_func):
    """
     Verrifies if:
     1. Question was not concluded previously
     2. Question is from student's schedules/class
     3. Question's schedule has not expired
    """
    def wrapped(request, *args, **kwargs):
        schedule_pk = kwargs.get('schedule_pk')
        question_pk = kwargs.get('question_pk')

        question = Question.objects.get(pk=question_pk)
        try:
            schedule = ListSchedule.objects.get(pk=schedule_pk)
        except ListSchedule.DoesNotExist:
            schedule = None

        if helpers.question_is_concluded(question, schedule, request.user.student):
            return HttpResponseRedirect(reverse_lazy('schedule_list'))
        elif schedule:
            if question not in schedule.question_list.questions.all() or \
                    request.user.student.active_class != schedule.course_class or schedule.is_closed:
                kwargs = {'schedule_pk': schedule_pk, 'pk': question_pk}
                return HttpResponseRedirect(reverse_lazy('question_detail_schedule', kwargs=kwargs))
        elif question.is_evaluative:
            return HttpResponseRedirect(reverse_lazy('subject_list'))

        return view_func(request, *args, **kwargs)

    return wrapped


def submission_author_or_professor_required(view_func):
    def wrapped(request, *args, **kwargs):

        if hasattr(request.user, 'professor'):
            return view_func(request, *args, **kwargs)

        submission = Submission.objects.get(pk=kwargs.get('pk'))

        if submission.student != request.user.student:
            return HttpResponseRedirect(reverse_lazy('submission_list'))
        else:
            return view_func(request, *args, **kwargs)

    return wrapped
