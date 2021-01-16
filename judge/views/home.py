from django.views.generic import TemplateView

from judge import helpers


class HomeView(TemplateView):
    template_name = 'judge/home.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        user = self.request.user
        return helpers.get_statistics(data, user)
