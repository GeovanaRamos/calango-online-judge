from django.urls import path
from django.views.generic import TemplateView
from judge import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('schedules/', views.ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/<pk>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    path('questions/<pk>/', views.QuestionDetailView.as_view(),  name='question_detail'),
    path('submissions/create/<question_pk>', views.SubmissionCreateView.as_view(), name='submission_create'),
    path('submissions/', views.SubmissionListView.as_view(), name='submission_list'),
    path('submissions/<pk>', views.SubmissionDetailView.as_view(), name='submission_detail'),
    path('classes/', views.ClassListView.as_view(), name='class_list'),
    path('questions/', views.QuestionListView.as_view(), name='question_list')
]
