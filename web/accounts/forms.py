from django import forms
from django.core.exceptions import ValidationError

from accounts.models import User


class EmailForm(forms.Form):
    email = forms.CharField()

    def clean(self):
        cd = self.cleaned_data

        if not User.objects.filter(email=cd.get('email')).exists():
            raise ValidationError('Este email não está cadastrado na plataforma.')
        elif not User.objects.get(email=cd.get('email')).is_active:
            raise ValidationError('Esta conta está inativa.')

        return cd
