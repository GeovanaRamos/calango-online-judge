from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.views.generic import FormView

from accounts.forms import EmailForm
from accounts.models import User
from coj import settings


class ForgotPasswordView(FormView):
    template_name = 'registration/forgot_password.html'
    form_class = EmailForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = User.objects.get(email=form.cleaned_data['email'])
        password = User.objects.make_random_password()
        user.set_password(password)

        subject = 'COJ - Recuperação de senha'
        data = {'full_name': user.full_name, 'password': password}
        html_message = render_to_string('registration/forgot_password_email.html', data)
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email, ]

        try:
            send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
        except Exception:
            messages.add_message(self.request, messages.ERROR, 'Erro ao enviar email. Contacte o administrador.')
        else:
            user.save()
            messages.add_message(self.request, messages.SUCCESS, 'Email enviado com sucesso!')

        return super(ForgotPasswordView, self).form_valid(form)



