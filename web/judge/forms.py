from ckeditor_uploader.widgets import CKEditorUploadingWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from dal_select2.widgets import ModelSelect2Multiple, ModelSelect2
from django import forms
from django.forms import inlineformset_factory

from judge import models
from judge.validators import validate_submission_syntehsis, validate_students


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ('code',)
        widgets = {
            'code': forms.Textarea(attrs={'rows': 20}),
        }

    def __init__(self, *args, **kwargs):
        self.course_class = kwargs.pop('course_class')
        super().__init__(*args, **kwargs)

    def clean(self):
        cd = self.cleaned_data
        if self.course_class.is_synthesis_required:
            cd = validate_submission_syntehsis(cd.get('code'))
        return cd


class ScheduleCreateForm(forms.ModelForm):
    class Meta:
        model = models.ListSchedule
        fields = '__all__'
        widgets = {'question_list': ModelSelect2(url='autocomplete_list')}

    def __init__(self, *args, **kwargs):
        self.professor = kwargs.pop('professor')
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

    def clean(self):
        cd = self.cleaned_data

        students_string = cd.get("students")
        students = students_string.splitlines()
        return validate_students(cd, students)


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
