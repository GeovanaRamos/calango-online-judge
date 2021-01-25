from django.contrib import admin
from judge import models


admin.site.register(models.CourseClass)
admin.site.register(models.Submission)
admin.site.register(models.QuestionList)
admin.site.register(models.TestCase)
admin.site.register(models.ListSchedule)


class TestCaseInline(admin.StackedInline):
    model = models.TestCase


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    model = models.Question
    inlines = [TestCaseInline]
