from django.urls import path

from accounts import views

urlpatterns = [
    path('forgot_password', views.ForgotPasswordView.as_view(), name='forgot_password'),
]
