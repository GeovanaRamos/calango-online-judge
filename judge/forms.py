from django import forms
from judge import models


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ('code',)
        widgets = {
            'code': forms.Textarea(attrs={'rows': 20}),
        }
