import csv
import re

from django.db.models import Count, Q, Case, When, F, Value, FloatField, IntegerField, Avg
from django.db.models.functions import Cast
from django.http import HttpResponse
from django.utils import timezone

from judge import models


def get_list_schedules_for_user(user):
    if hasattr(user, 'student'):
        # show list of the student's active class
        current_class = user.student.active_class
        return models.ListSchedule.objects.filter(
            course_class=current_class,
            start_date__lte=timezone.localtime()
        ).order_by('-start_date', 'due_date')
    elif hasattr(user, 'professor'):
        # show list of all of the professor's active classes
        classes = user.professor.active_classes
        return models.ListSchedule.objects.filter(
            course_class__in=classes).distinct().order_by('-start_date', 'due_date')
    elif user.is_superuser:
        return models.ListSchedule.objects.all()
    else:
        return models.ListSchedule.objects.none()


def get_submissions_for_user_and_schedules(user, schedules):
    if hasattr(user, 'student'):
        student = user.student
        return models.Submission.objects.filter(
            student=student, list_schedule__in=schedules.all()).distinct()
    else:
        return models.Submission.objects.filter(
            list_schedule__in=schedules.all()).distinct()


def get_question_status_for_user(user, question, list_schedule):
    if hasattr(user, 'student'):
        # returns the result of the submission
        submission = models.Submission.objects.filter(student=user.student, question=question,
                                                      list_schedule=list_schedule)
        if submission.exists():
            return submission.latest('submitted_at').get_result_display()
        else:
            return models.Submission.NO_SUBMISSION_LABEL
    else:
        # returns the count of accepted submissions of the class
        submissions = models.Submission.objects.filter(
            result=models.Submission.Results.ACCEPTED,
            question=question,
            list_schedule=list_schedule,
        )
        return submissions.count()


def question_is_concluded(question, list_schedule, student):
    if list_schedule:
        if models.Submission.objects.filter(question=question, student=student, list_schedule=list_schedule,
                                            result=models.Submission.Results.ACCEPTED).exists():
            return True
    elif models.Submission.objects.filter(question=question, student=student, course_class=student.active_class,
                                          result=models.Submission.Results.ACCEPTED).exists():
        return True

    return False


def get_schedule_question_info_for_user(list_schedule, user):
    questions = list_schedule.question_list.questions.order_by('pk').all()
    question_conclusions = []
    for question in questions:
        question.result = get_question_status_for_user(user, question, list_schedule)
        question_conclusions.append(question)
    return question_conclusions


def get_final_percentage_for_student(schedules, student):
    questions_count = models.Question.objects.filter(lists__schedules__in=schedules).count()
    if questions_count == 0:
        return 0
    accepted_count = models.Submission.objects.filter(
        student=student, result=models.Submission.Results.ACCEPTED,
        list_schedule__in=schedules).count()
    return accepted_count * 100 / questions_count


def get_attempts_average_for_student(schedules, student):
    submissions = Count('submissions', filter=Q(submissions__list_schedule__in=schedules.all()))
    student = models.Student.objects.filter(
        pk=student.pk).values('registration_number', 'submissions__question').annotate(
        submissions_count=submissions).exclude(submissions_count=0)
    return student.aggregate(Avg('submissions_count'))['submissions_count__avg']


def get_attempts_average_for_class(schedules, course_class, user):
    submissions = Count('submissions', filter=Q(submissions__list_schedule__in=schedules.all()))
    students = course_class.students.exclude(user=user).values('registration_number', 'submissions__question').annotate(
        submissions_count=submissions).exclude(submissions_count=0)
    return students.aggregate(Avg('submissions_count'))['submissions_count__avg']


def get_students_and_results(list_schedule, students):
    list_questions_count = list_schedule.question_list.questions.count()

    for question in list_schedule.question_list.questions.all().order_by('pk'):
        # for each question from the schedule, gather student submission count and status
        accepted_subs = Count('submissions',
                              filter=Q(submissions__result=models.Submission.Results.ACCEPTED) & Q(
                                  submissions__question=question) & Q(submissions__list_schedule=list_schedule))
        count_subs = Count('submissions',
                           filter=Q(submissions__question=question) & Q(submissions__list_schedule=list_schedule))

        # dynamic labels for the json parsed at the template
        str_pk = str(question.pk)
        label1 = '#' + str_pk
        label2 = str_pk + '-A'
        label3 = str_pk + '-S'

        # get the submission status based on accepted and total count
        status = Case(
            When(**{'{0}__{1}'.format(label2, 'gte'): 1}, then=models.Submission.ACCEPTED),
            When(**{'{0}__{1}'.format(label1, 'gte'): 1}, then=models.Submission.UNACCEPTED),
            default=Value(models.Submission.NO_SUBMISSION)
        )

        # add results from question[i] to final query
        students = students.annotate(**{label1: count_subs}).annotate(**{label2: accepted_subs}).annotate(
            **{label3: Cast(status, IntegerField())})

    # get student percentage based on all questions from the schedule
    accepted_total = Count('submissions',
                           filter=Q(submissions__result=models.Submission.Results.ACCEPTED) & Q(
                               submissions__list_schedule=list_schedule))
    students = students.annotate(full_name=F('user__full_name')).annotate(
        percentage=Cast(accepted_total / float(list_questions_count) * 100, FloatField()))

    return students.values()


def get_all_active_submissions_for_student(student):
    schedules = student.active_class.schedules if student.active_class else models.ListSchedule.objects.none()
    evaluative = get_submissions_for_user_and_schedules(student.user, schedules)
    non_evaluative = models.Submission.objects.filter(student=student, course_class=student.active_class)
    submissions = evaluative.union(non_evaluative)
    return submissions.order_by('-submitted_at')


def get_judge_post_data(code, question_pk):
    test_cases = models.TestCase.objects.filter(question__pk=question_pk)

    cases = []
    for case in test_cases:
        cases.append({
            "input": re.split('\s*\\n\s*', case.inputs.replace("\r", "")),
            "output": case.output.replace("\r", "")
        })

    return {"code": code, "cases": cases}


def export_csv_file(students, list_schedule):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=' + list_schedule.__str__() + '.csv'

    writer = csv.writer(response)
    header = ['matricula', 'nome']
    for question in list_schedule.question_list.questions.all().order_by('pk'):
        header.append('#' + str(question.pk))
    header.append('percentual_na_lista')
    writer.writerow(header)

    for student in students:
        row = [student['registration_number'], student['full_name']]
        for key, value in student.items():
            if key[-1] == 'A':
                row.append(value)
        row.append(student['percentage'])
        writer.writerow(row)

    return response


def export_csv_file_for_all_class_lists(class_pk):
    course_class = models.CourseClass.objects.get(pk=class_pk)
    columns = []

    registration_number = ['matricula']
    names = ['nome']
    for student in course_class.students.order_by('registration_number'):
        registration_number.append(student.registration_number)
        names.append(student.user.full_name)

    columns.append(registration_number)
    columns.append(names)

    for schedule in course_class.schedules.order_by('pk'):
        column = [schedule.question_list.name]
        results = get_students_and_results(schedule, course_class.students.order_by('registration_number'))
        for result in results:
            column.append(result['percentage'])
        columns.append(column)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=' + course_class.__str__() + '.csv'

    final_result = zip(*columns)

    writer = csv.writer(response)
    for row in final_result:
        writer.writerow(row)

    return response


def search_submissions(user, id, student_name, student_number, question_id, question_name):
    if id or student_name or student_number or question_id or question_name:
        schedules = get_list_schedules_for_user(user)
        submissions = get_submissions_for_user_and_schedules(user, schedules)
        if id:
            submissions = submissions.filter(pk=int(id))
        if student_name:
            submissions = submissions.filter(student__user__full_name__icontains=student_name)
        if student_number:
            submissions = submissions.filter(student__registration_number=int(student_number))
        if question_id:
            submissions = submissions.filter(question__pk=int(question_id))
        if question_name:
            submissions = submissions.filter(question__name__icontains=question_name)
        return submissions.order_by('-submitted_at')[:100]
    else:
        return models.Submission.objects.none()
