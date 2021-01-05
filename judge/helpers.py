from judge import models


def get_user_classes(user):
    if hasattr(user, 'student'):
        return user.student.classes.all().order_by('-year', '-semester').filter(is_active=True)
    elif hasattr(user, 'professor'):
        return models.CourseClass.objects.filter(teacher=user.professor).order_by('-year', '-semester')
    else:
        return models.CourseClass.objects.none()


def get_course_class_questions(course_class):
    questions = models.Question.objects.none()
    lists = models.ListSchedule.objects.filter(course_class=course_class)
    for lst in lists:
        questions = questions | lst.question_list.questions.all()

    return questions


def get_student_question_status(student, question):
    submission = models.Submission.objects.filter(student=student, question=question)
    if submission.exists():
        return submission.latest('judged_at').get_result_display()
    else:
        return "Sem Submissão"


def student_has_concluded_list_schedule(student, list_schedule):
    questions = list_schedule.question_list.questions
    submissions = models.Submission.objects.filter(
        student=student, question__in=questions.all(), result=models.Submission.Results.ACCEPTED)
    return submissions.count() >= questions.count()
