from django.urls import path

from judge import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('dashborad/class/<int:class_pk>', views.HomeView.as_view(), name='home'),
    path('help/', views.HelpView.as_view(), name='help'),

    path('schedules/', views.ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/<int:pk>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    path('schedules/create/', views.ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/update/<int:pk>/', views.ScheduleUpdateView.as_view(), name='schedule_update'),
    path('schedules/delete/<int:pk>/', views.ScheduleDeleteView.as_view(), name='schedule_delete'),
    path('schedules/<int:pk>/results/', views.ResultsDetailView.as_view(), name='results_detail'),
    path('schedules/<int:schedule_pk>/questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),

    path('lists/create/', views.ListCreateView.as_view(), name='list_create'),

    path('subjects/', views.SubjectsListView.as_view(), name='subject_list'),
    path('questions/create/', views.QuestionCreateView.as_view(), name='question_create'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('questions/<subject>/', views.QuestionListView.as_view(), name='question_list'),


    path('submissions/', views.SubmissionListView.as_view(), name='submission_list'),
    path('submissions/<int:pk>/', views.SubmissionDetailView.as_view(), name='submission_detail'),
    path('schedules/<schedule_pk>/questions/<question_pk>/submissions/create/', views.SubmissionCreateView.as_view(),
         name='submission_create'),
    path('submissions/schedule/<schedule_pk>/student/<student_pk>/', views.SubmissionListView.as_view(),
         name='submission_list'),
    path('submissions/test/', views.SubmissionTest.as_view(), name='submission_test'),

    path('classes/', views.ClassListView.as_view(), name='class_list'),
    path('classes/create/', views.ClassCreateView.as_view(), name='class_create'),
    path('classes/delete/<int:pk>/', views.ClassDeleteView.as_view(), name='class_delete'),
    path('classes/<int:class_pk>/students/create/', views.StudentFormView.as_view(), name='student_form'),
    path('classes/<int:class_pk>/students/', views.StudentListView.as_view(), name='student_list'),
    path('classes/<int:class_pk>/students/delete/<int:pk>/', views.StudentDeleteView.as_view(), name='student_delete'),
]
