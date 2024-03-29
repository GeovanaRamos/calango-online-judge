from django.urls import path

from judge import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('help/', views.HelpView.as_view(), name='help'),
    path('classes/<int:class_pk>/statistics/', views.StatisticsView.as_view(), name='class_statistics'),

    path('schedules/', views.ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/<int:pk>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    path('classes/<int:class_pk>/schedules/<int:pk>', views.ScheduleClassDetailView.as_view(),
         name='schedule_class_detail'),
    path('schedules/create/', views.ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/update/<int:pk>/', views.ScheduleUpdateView.as_view(), name='schedule_update'),
    path('schedules/delete/<int:pk>/', views.ScheduleDeleteView.as_view(), name='schedule_delete'),
    path('schedules/<int:pk>/results/', views.ResultsDetailView.as_view(), name='results_detail'),
    path('classes/<int:class_pk>/schedules/<int:pk>/results/', views.ResultsDetailView.as_view(),
         name='results_class_detail'),
    path('schedules/<int:schedule_pk>/questions/<int:pk>/', views.QuestionDetailView.as_view(),
         name='question_detail_schedule'),

    path('lists/create/', views.ListCreateView.as_view(), name='list_create'),

    path('subjects/', views.SubjectsListView.as_view(), name='subject_list'),
    path('questions/create/', views.QuestionCreateView.as_view(), name='question_create'),
    path('questions/update/<int:pk>', views.QuestionUpdateView.as_view(), name='question_update'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('questions/<subject>/', views.QuestionListView.as_view(), name='question_list'),

    path('submissions/', views.SubmissionListView.as_view(), name='submission_list'),
    path('submissions/<int:pk>/', views.SubmissionDetailView.as_view(), name='submission_detail'),
    path('schedules/<schedule_pk>/questions/<question_pk>/submissions/create/', views.SubmissionCreateView.as_view(),
         name='submission_create_schedule'),
    path('questions/<question_pk>/submissions/create/', views.SubmissionCreateView.as_view(),
         name='submission_create'),
    path('submissions/schedule/<schedule_pk>/student/<student_pk>/', views.SubmissionListView.as_view(),
         name='submission_list'),
    path('submissions/test/', views.SubmissionTest.as_view(), name='submission_test'),

    path('classes/', views.ClassListView.as_view(), name='class_list'),
    path('classes/inactive/', views.ClassInactiveListView.as_view(), name='class_inactive_list'),
    path('classes/create/', views.ClassCreateView.as_view(), name='class_create'),
    path('classes/update/<int:pk>', views.ClassUpdateView.as_view(), name='class_update'),
    path('classes/deactivate/<int:pk>/', views.ClassDeleteView.as_view(), name='class_delete'),
    path('classes/<int:class_pk>/students/create/', views.StudentFormView.as_view(), name='student_form'),
    path('classes/<int:class_pk>/students/', views.StudentListView.as_view(), name='student_list'),
    path('classes/<int:class_pk>/students/remove/<int:pk>/', views.StudentDeleteView.as_view(), name='student_delete'),
    path('classes/<int:class_pk>/activities/', views.ActivitiesView.as_view(), name='class_activities'),
    path('classes/activities/questions/', views.StudentQuestionsResults.as_view(), name='class_activities_questions'),

    path('autocomplete/questions/', views.QuestionAutocomplete.as_view(), name='autocomplete_question'),
    path('autocomplete/lists/', views.ListAutocomplete.as_view(), name='autocomplete_list'),
]
