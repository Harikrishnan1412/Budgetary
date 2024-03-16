from django.urls import path
from .views import RegistrationView, send1_email, UsernameValidationView, VerificationView, CompletePasswordReset, RequestPasswordReset, EmailValidationView, LoginView, LogoutView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register', RegistrationView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
    path('request-password', RequestPasswordReset.as_view(), name='request-password'),
    path('send_email', send1_email, name='send_email'),
    path('reset-user-password/<uidb64>/<token>', CompletePasswordReset.as_view(), name='reset-user-password'),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate')
]
        