from django.contrib import admin
from judge import models
from judge.forms import QuestionForm, TestCaseForm

admin.site.register(models.CourseClass)
admin.site.register(models.Submission)
admin.site.register(models.QuestionList)
admin.site.register(models.TestCase)
admin.site.register(models.ListSchedule)


class TestCaseInline(admin.StackedInline):
    model = models.TestCase
    form = TestCaseForm


class AuthorQuestionForm(QuestionForm):
    class Meta:
        model = models.Question
        fields = '__all__'


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    model = models.Question
    form = AuthorQuestionForm
    inlines = [TestCaseInline]
