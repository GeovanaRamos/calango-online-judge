from django import forms
from judge import models


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ('code',)
        widgets = {
            'code': forms.Textarea(attrs={'rows': 20}),
        }


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = models.ListSchedule
        fields = '__all__'


class ListForm(forms.ModelForm):
    class Meta:
        model = models.QuestionList
        fields = '__all__'


class ClassForm(forms.ModelForm):
    class Meta:
        model = models.CourseClass
        exclude = ('professor', 'is_active',)
