import random
from django.core.mail import send_mail
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


# 1. Custom Registration Form with Bootstrap Styling Injection
class CustomUserCreationForm(UserCreationForm):

  class Meta(UserCreationForm.Meta):
    model = User
    fields = ('username', 'first_name', 'email')

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
      field.widget.attrs['class'] = 'form-control'


# Step 1: Register website user, set inactive, and send OTP via email backend
def register_view(request):
  if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      # Save user temporarily as inactive until OTP is verified
      user = form.save(commit=False)
      user.is_active = False
      user.save()

      # Generate 6-digit OTP
      otp = str(random.randint(100000, 999999))

      # Store data in session
      request.session['pending_user_id'] = user.id
      request.session['generated_otp'] = otp

      # Send OTP email (outputs to your terminal console)
      send_mail(
          subject='Plexus Electro CRM - Email Verification OTP',
          message=(
              f'Hello {user.first_name},\n\nYour registration verification code'
              f' is: {otp}\n\nEnter this code on the website to activate your'
              ' Plexus Electro CRM account.'
          ),
          from_email='no-reply@plexuselectro.com',
          recipient_list=[user.email],
          fail_silently=False,
      )

      return redirect('verify_otp')
  else:
    form = CustomUserCreationForm()
  return render(request, 'main/register.html', {'form': form})


# Step 2: Verify OTP and activate the website account
def verify_otp_view(request):
  if request.method == 'POST':
    # Use .strip() to avoid accidental spaces typed by the user
    entered_otp = request.POST.get('otp', '').strip()
    saved_otp = str(request.session.get('generated_otp', '')).strip()
    user_id = request.session.get('pending_user_id')

    # Check if session expired or data is missing
    if not saved_otp or not user_id:
      error = 'Session expired or invalid. Please register again.'
      return render(request, 'main/verify_otp.html', {'error': error})

    if entered_otp == saved_otp:
      try:
        user = User.objects.get(id=user_id)
        user.is_active = True  # Activate account successfully
        user.save()

        # Clear session data safely
        request.session.pop('pending_user_id', None)
        request.session.pop('generated_otp', None)

        # Log user in directly after verification
        login(request, user)
        return redirect('dashboard')
      except User.DoesNotExist:
        error = 'User account not found. Please register again.'
        return render(request, 'main/verify_otp.html', {'error': error})
    else:
      error = (
          'Invalid OTP code. Please check the code printed in your terminal'
          ' and try again.'
      )
      return render(request, 'main/verify_otp.html', {'error': error})

  return render(request, 'main/verify_otp.html')


# 2. Custom Password Reset Form (Bootstrap styling injection)
class CustomPasswordResetForm(PasswordResetForm):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
      field.widget.attrs['class'] = 'form-control'


# 3. Secure Dashboard View
@login_required
def dashboard_view(request):
  return render(request, 'main/dashboard.html')