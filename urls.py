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
    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/add/', views.add_customer_view, name='add_customer'),
    path(
        'customers/<int:pk>/edit/',
        views.edit_customer_view,
        name='edit_customer',
    ),
    path(
        'customers/<int:pk>/delete/',
        views.delete_customer_view,
        name='delete_customer',
    ),
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
        'edit-employee/<int:employee_id>/',
        views.edit_employee_view,
        name='edit_employee',
    ),
    path(
        'delete-employee/<int:employee_id>/',
        views.delete_employee_view,
        name='delete_employee',
    ),
    path('products/', views.product_list_view, name='product_list'),
    path('categories/', views.category_list_view, name='category_list'),
    path(
        'add-category/', views.add_category_view, name='add_category'
    ),  # Category view
    path('add-product/', views.add_product_view, name='add_product'),
    path(
        'categories/edit/<int:pk>/',
        views.edit_category_view,
        name='edit_category',
    ),
    path(
        'categories/delete/<int:pk>/',
        views.delete_category_view,
        name='delete_category',
    ),
    path(
    'products/<int:pk>/edit/', views.edit_product_view, name='edit_product'
),
path(
    'products/<int:pk>/delete/',
    views.delete_product_view,
    name='delete_product',
),
]