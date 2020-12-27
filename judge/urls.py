from django.urls import path
from django.views.generic import TemplateView
from judge import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='judge/home.html'), name='home'),
    path('schedules/', views.ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/<pk>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    path('questions/<pk>', views.QuestionDetailView.as_view(),  name='question_detail'),
]
