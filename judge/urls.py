from django.urls import path
from django.views.generic import TemplateView
from judge import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='judge/home.html'), name='home'),
    path('applications/', views.ListScheduleListView.as_view(), name='list_schedule_list')
]
