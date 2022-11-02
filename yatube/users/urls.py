from django.contrib.auth import views
from django.urls import path

from users.apps import UsersConfig
from users.views import SignUp

app_name = UsersConfig.name

urlpatterns = [
    path(
        'signup/',
        SignUp.as_view(template_name='users/signup.html'),
        name='signup',
    ),
    path(
        'logout/',
        views.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout',
    ),
    path(
        'login/',
        views.LoginView.as_view(template_name='users/login.html'),
        name='login',
    ),
    path(
        'password_reset/',
        views.PasswordResetView.as_view(),
        name='password_reset',
    ),
]
