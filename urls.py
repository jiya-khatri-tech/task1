from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView
from main.views import dashboard_view  # <--- 1. Import your dashboard view

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),  # <--- 2. Add the dashboard route
]