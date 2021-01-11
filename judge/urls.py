from django.urls import path
from judge import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('schedules/', views.ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/<pk>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    path('questions/<pk>/', views.QuestionDetailView.as_view(),  name='question_detail'),
    path('submissions/create/<question_pk>/', views.SubmissionCreateView.as_view(), name='submission_create'),
    path('submissions/', views.SubmissionListView.as_view(), name='submission_list'),
    path('submissions/<pk>/', views.SubmissionDetailView.as_view(), name='submission_detail'),
    path('classes/', views.ClassListView.as_view(), name='class_list'),
    path('questions/', views.QuestionListView.as_view(), name='question_list'),
    path('lists/create/', views.ListCreateView.as_view(), name='list_create'),
    path('schedules/create', views.ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/update/<pk>/', views.ScheduleUpdateView.as_view(), name='schedule_update'),
    path('schedules/delete/<pk>/', views.ScheduleDeleteView.as_view(), name='schedule_delete'),
    path('schedules/<pk>/results/', views.ResultsDetailView.as_view(), name='results_detail'),
    path('classes/create', views.ClassCreateView.as_view(), name='class_create'),
    path('classes/<class_pk>/students/create', views.StudentFormView.as_view(), name='student_form'),
    path('classes/<class_pk>/students', views.StudentListView.as_view(), name='student_list')
]
