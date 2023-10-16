from django.contrib.auth.views import LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import RegisterView, verify_email, verification_failed, CustomLoginView, verification_pass, \
    CustomPasswordResetView, CustomPasswordResetConfirmView, CustomPasswordResetDoneView, \
    CustomPasswordResetCompleteView

app_name = UsersConfig.name


urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify_email/<str:uidb64>/<str:token>/', verify_email, name='verify_email'),
    path('verification_failed/', verification_failed, name='verification_failed'),
    path('verification_pass/', verification_pass, name='verification_pass'),
    path('reset_password/', CustomPasswordResetView.as_view(template_name='users/reset_password.html'), name='reset_password'),
    path('reset_password_sent/', CustomPasswordResetDoneView.as_view(template_name='users/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>', CustomPasswordResetConfirmView.as_view(template_name='users/password_reset_form.html'), name='password_reset_confirm'),
    path('reset/password_complete', CustomPasswordResetCompleteView.as_view(template_name='users/password_reset_done.html'), name='password_reset_complete'),
]
