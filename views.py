from django.contrib.auth import login
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


# 1. Custom Registration Form (handles name, email, username, password)
class CustomUserCreationForm(UserCreationForm):

  class Meta(UserCreationForm.Meta):
    model = User
    fields = ('username', 'first_name', 'email')

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
      field.widget.attrs['class'] = 'form-control'


def register_view(request):
  if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('dashboard')
  else:
    form = CustomUserCreationForm()
  return render(request, 'main/register.html', {'form': form})


# 2. Custom Password Reset Form (adds Bootstrap styling to the email input)
class CustomPasswordResetForm(PasswordResetForm):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
      field.widget.attrs['class'] = 'form-control'


# 3. Dashboard View
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
  return render(request, 'main/dashboard.html')