import csv
import re

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


def student_has_concluded_list_schedule(student, list_schedule):
    questions = list_schedule.question_list.questions.all()
    submissions = models.Submission.objects.filter(
        student=student, question__in=questions, result=models.Submission.Results.ACCEPTED,
        list_schedule=list_schedule).distinct()
    return submissions.count() >= questions.count()


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
            return models.Submission.NO_SUBMISSION
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


def get_student_acceptance_percentage(student, list_schedule):
    count, correct = 0, 0
    for question in list_schedule.question_list.questions.all():
        question.result = get_question_status_for_user(student.user, question, list_schedule)
        if question.result == models.Submission.Results.ACCEPTED.label:
            correct += 1
        count += 1

    return correct / count * 100


def get_schedule_question_info_for_user(list_schedule, user):
    questions = list_schedule.question_list.questions.order_by('pk').all()
    question_conclusions = []
    for question in questions:
        question.result = get_question_status_for_user(user, question, list_schedule)
        question_conclusions.append(question)
    return question_conclusions


def get_students_and_results(list_schedule):
    students = []
    for s in list_schedule.course_class.students.all():
        s.questions = list_schedule.question_list.questions.all()
        count, correct = 0, 0
        for q in s.questions:
            q.sub_count = models.Submission.objects.filter(student=s, question=q, list_schedule=list_schedule).count()
            q.result = get_question_status_for_user(s.user, q, list_schedule)
            if q.result == models.Submission.Results.ACCEPTED.label:
                correct += 1
            count += 1
        s.percentage = correct / count * 100
        students.append(s)
    return students


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

    for student in students:
        writer.writerow([student.registration_number, student.user.full_name, student.percentage])

    return response
