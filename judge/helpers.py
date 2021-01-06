from django.db.models import Count

from judge import models


def get_student_active_class(student):
    return student.classes.all().filter(is_active=True).first()


def get_professor_classes(professor):
    return models.CourseClass.objects.filter(
        professor=professor,
        is_active=True
    ).order_by('-year', '-semester')


def get_list_schedules_for_user(user):
    if hasattr(user, 'student'):
        # show list of one of the student's active class
        current_class = get_student_active_class(user.student)
        return models.ListSchedule.objects.filter(course_class=current_class)
    elif hasattr(user, 'professor'):
        # show list of all of the professor's active classes
        classes = get_professor_classes(user.professor)
        return models.ListSchedule.objects.filter(course_class__in=classes)
    elif user.is_superuser:
        return models.ListSchedule.objects.all()
    else:
        return models.ListSchedule.objects.none()


def student_has_concluded_list_schedule(student, list_schedule):
    questions = list_schedule.question_list.questions
    submissions = models.Submission.objects.filter(
        student=student, question__in=questions.all(), result=models.Submission.Results.ACCEPTED)
    return submissions.count() >= questions.count()


def get_list_schedule_conclusions(list_schedules, user):
    conclusions = 0
    if hasattr(user, 'student'):
        # show conclusions of student in the lists of the active class
        for ls in list_schedules:
            if student_has_concluded_list_schedule(user.student, ls):
                conclusions += 1
        return conclusions
    elif hasattr(user, 'professor') or user.is_superuser:
        # show conclusions of the professor's active classes
        for ls in list_schedules:
            students = ls.course_class.students.all()
            for student in students:
                if student_has_concluded_list_schedule(student, ls):
                    conclusions += 1
        return conclusions
    else:
        return 0


def get_questions_for_list_schedules(list_schedules):
    # questions = models.Question.objects.none()
    #
    # for lst in list_schedules:
    #     questions = questions | lst.question_list.questions.all()

    return models.Question.objects.filter(lists__schedules__in=list_schedules).count()


def get_submissions_results_for_user(user):
    submissions = models.Submission.objects.none()

    if hasattr(user, 'student'):
        # show submissions of student in the lists of the active class
        submissions = models.Submission.objects.filter(student=user.student)
        return submissions.values('result').annotate(count=Count('result'))
    elif hasattr(user, 'professor') or user.is_superuser:
        # show submissions of the professor's active classes
        classes = get_professor_classes(user.professor)
        submissions = models.Submission.objects.filter(student__classes__in=classes)
        return submissions.values('result').annotate(count=Count('result'))
    else:
        return 0


def get_question_status_for_student(student, question):
    submission = models.Submission.objects.filter(student=student, question=question)
    if submission.exists():
        return submission.latest('judged_at').get_result_display()
    else:
        return "Sem Submissão"
