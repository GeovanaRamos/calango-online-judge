from django.db.models import Count, Sum
from django.utils import timezone

from judge import models


def get_list_schedules_for_user(user):
    if hasattr(user, 'student'):
        # show list of the student's active class
        current_class = user.student.active_class
        return models.ListSchedule.objects.filter(course_class=current_class).order_by('-start_date', 'due_date')
    elif hasattr(user, 'professor'):
        # show list of all of the professor's classes
        classes = user.professor.classes.all()
        return models.ListSchedule.objects.filter(course_class__in=classes).distinct().order_by('-start_date',
                                                                                                'due_date')
    elif user.is_superuser:
        return models.ListSchedule.objects.all()
    else:
        return models.ListSchedule.objects.none()


def student_has_concluded_list_schedule(student, list_schedule):
    questions = list_schedule.question_list.questions.all()
    submissions = models.Submission.objects.filter(
        student=student, question__in=questions, result=models.Submission.Results.ACCEPTED,
        list_schedule=list_schedule).distinct()
    return submissions.count() >= questions.count()


# STATISTICS ONLY
def get_list_schedule_conclusions(list_schedules, user):
    conclusions = 0
    if hasattr(user, 'student'):
        # show conclusions of student in the lists of the active class
        for ls in list_schedules:
            if student_has_concluded_list_schedule(user.student, ls):
                conclusions += 1
        return conclusions
    elif hasattr(user, 'professor') or user.is_superuser:
        # show students' conclusions of the professor's classes
        for ls in list_schedules:
            students = ls.course_class.students.all()
            for student in students:
                if student_has_concluded_list_schedule(student, ls):
                    conclusions += 1
        return conclusions
    else:
        return 0


# STATISTICS ONLY
def get_questions_for_list_schedules(list_schedules):
    return models.Question.objects.filter(
        lists__schedules__in=list_schedules).distinct().count()


# STATISTICS ONLY
def get_submissions_results_for_user(user):
    if hasattr(user, 'student'):
        # show submissions of student in the lists of the active class
        submissions = models.Submission.objects.filter(student=user.student)
        return submissions.values('result').annotate(count=Count('pk', distinct=True))
    elif hasattr(user, 'professor') or user.is_superuser:
        # show submissions of the professor's classes
        classes = user.professor.classes.all()
        submissions = models.Submission.objects.filter(student__classes__in=classes).distinct()
        return submissions.values('result').annotate(count=Count('pk', distinct=True))
    else:
        return 0


def get_question_status_for_user(user, question, list_schedule):
    if hasattr(user, 'student'):
        # returns the result of the submission
        submission = models.Submission.objects.filter(student=user.student, question=question,
                                                      list_schedule=list_schedule)
        if submission.exists():
            return submission.latest('judged_at').get_result_display()
        else:
            return "Sem Submissão"
    else:
        # returns the count of accepted submissions of the class
        submissions = models.Submission.objects.filter(
            result=models.Submission.Results.ACCEPTED,
            question=question,
            list_schedule=list_schedule,
        )
        return submissions.count()


def get_submissions_for_user(user):
    if hasattr(user, 'student'):
        # returns student's submissions
        course_class = user.student.active_class
        return models.Submission.objects.filter(
            student=user.student,
            student__classes=course_class,
        ).distinct().order_by('-submitted_at')
    else:
        # returns first 20 submissions
        return models.Submission.objects.all()[:20]


def get_questions_for_user(user):
    if hasattr(user, 'professor'):
        return models.Question.objects.all()
    else:
        # returns all submissions
        return models.Submission.objects.none()


def get_statistics(data, user):
    lists = get_list_schedules_for_user(user)  # TODO professor ativas

    # BOX
    data['count_lists'] = lists.count()
    data['count_questions'] = get_questions_for_list_schedules(lists)

    # CHART
    data['count_concluded'] = get_list_schedule_conclusions(lists, user)  # TODO professor ativas
    data['count_pending'] = data['count_lists'] - data['count_concluded']  # TODO professor ativas

    submissions_results = get_submissions_results_for_user(user)  # TODO professor ativas

    data['result_labels'] = []
    data['result_values'] = []
    data['count_submissions'] = 0
    for counting_obj in submissions_results:
        if counting_obj['result']:
            data['result_labels'].append(models.Submission.Results(counting_obj['result']).label)
            data['result_values'].append(counting_obj['count'])
            data['count_submissions'] += counting_obj['count']

    return data


def question_is_open_to_submit(question, list_schedule, student):
    if models.Submission.objects.filter(question=question, student=student,
                                        list_schedule=list_schedule, result=models.Submission.Results.ACCEPTED
                                        ).exists():
        return False
    elif timezone.localtime() > list_schedule.due_date or timezone.localtime() < list_schedule.start_date:
        return False

    return True
