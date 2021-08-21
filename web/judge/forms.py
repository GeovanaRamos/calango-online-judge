import re

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from dal_select2.widgets import ModelSelect2Multiple, ModelSelect2
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from judge import models


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ('code',)
        widgets = {
            'code': forms.Textarea(attrs={'rows': 20}),
        }


class ScheduleCreateForm(forms.ModelForm):
    class Meta:
        model = models.ListSchedule
        fields = '__all__'
        widgets = {'question_list': ModelSelect2(url='autocomplete_list')}

    def __init__(self, *args, **kwargs):
        self.professor = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['course_class'].queryset = models.CourseClass.objects.filter(
            professor=self.professor, is_active=True)
        self.fields['question_list'].queryset = models.QuestionList.objects.filter(
            author=self.professor)


class ScheduleUpdateForm(forms.ModelForm):
    class Meta:
        model = models.ListSchedule
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course_class'].disabled = True
        self.fields['question_list'].disabled = True


class ListForm(forms.ModelForm):
    class Meta:
        model = models.QuestionList
        exclude = ('author',)
        widgets = {'questions': ModelSelect2Multiple(url='autocomplete_question')}


class ClassForm(forms.ModelForm):
    class Meta:
        model = models.CourseClass
        exclude = ('professor', 'is_active', 'students')


class StudentForm(forms.Form):
    students = forms.CharField(label='Alunos', help_text='Adicione alunos em formato csv (separador=;)',
                               widget=forms.Textarea)

    def validate_registration_number(self, registration):
        number = registration.replace('/', '')
        try:
            return int(number)
        except ValueError:
            raise ValidationError("Existe uma matrícula não válida: " + number)

    def create_email(self, registration):
        return str(registration) + "@aluno.unb.br"

    def clean(self):

        cd = self.cleaned_data

        students_string = cd.get("students")
        students = students_string.splitlines()

        cd['students'] = []
        for s in students:
            student_data = re.split('\s*;\s*', s)
            registration_number = self.validate_registration_number(student_data[0])
            full_name = student_data[1]
            email = self.create_email(registration_number)
            cd['students'].append([email, full_name, registration_number])

        return cd


class QuestionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget(), label='Descrição')

    class Meta:
        model = models.Question
        exclude = ('author',)


class TestCaseForm(forms.ModelForm):
    output = forms.CharField(strip=False, label='Saída', widget=forms.Textarea)

    class Meta:
        model = models.TestCase
        exclude = ('question',)


class TestCaseFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.form_method = 'post'
        self.layout = Layout(
            Div(
                Div('inputs', css_class='col-md-6'),
                Div('output', css_class='col-md-6'),
                css_class='row',
            ),
            Div('is_hidden', css_class='text-center'),
        )


TestCasesFormSet = inlineformset_factory(
    models.Question, models.TestCase, form=TestCaseForm, extra=1, can_delete=False
)
