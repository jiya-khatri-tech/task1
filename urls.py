from django.urls import path
from . import views

urlpatterns = [
    # Registration & OTP
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    # Authentication & Dashboard
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    # Password Reset Flow
    path(
        'forgot-password/',
        views.forgot_password_request_view,
        name='forgot_password',
    ),
    path(
        'verify-reset-otp/',
        views.verify_reset_otp_view,
        name='verify_reset_otp',
    ),
    path(
        'reset-password/',
        views.reset_password_form_view,
        name='reset_password_form',
    ),
    path(
        'register-employee/',
        views.admin_register_employee_view,
        name='admin_register_employee',
    ),
    path('employees/', views.employee_list_view, name='employee_list'),
    path(
        'register-employee/',
        views.admin_register_employee_view,
        name='admin_register_employee',
    ),
    path(
        'edit-employee/<int:employee_id>/',
        views.edit_employee_view,
        name='edit_employee',
    ),
    path(
        'delete-employee/<int:employee_id>/',
        views.delete_employee_view,
        name='delete_employee',
    ),
]