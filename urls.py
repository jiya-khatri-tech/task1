from django.contrib.auth import views as auth_views
from django.urls import path
from .views import (
    CustomPasswordResetForm,
    dashboard_view,
    register_view,
    verify_otp_view,
)

urlpatterns = [
    # Website Authentication & Navigation
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='main/login.html'),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout',
    ),
    path('register/', register_view, name='register'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Password Reset Workflow
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='main/password_reset.html',
            form_class=CustomPasswordResetForm,
        ),
        name='password_reset',
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='main/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='main/password_reset_confirm.html'
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='main/password_reset_complete.html'
        ),
        name='reset_done',
    ),
]