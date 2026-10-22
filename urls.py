from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    # 1. Redirect root URL '/' to '/login/' automatically
    path('', RedirectView.as_view(url='login/', permanent=False)),
    
    # 2. Django admin site
    path('admin/', admin.site.urls),
    
    # 3. THIS WAS MISSING: The custom Login route
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    
    # 4. Logout route
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]