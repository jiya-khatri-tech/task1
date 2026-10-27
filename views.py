import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render


# ==========================================
# 1. REGISTRATION & EMAIL OTP VERIFICATION
# ==========================================


def register_view(request):
  if request.method == 'POST':
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()

    if User.objects.filter(username=username).exists():
      return render(
          request, 'main/register.html', {'error': 'Username already exists.'}
      )
    if User.objects.filter(email=email).exists():
      return render(
          request, 'main/register.html', {'error': 'Email already exists.'}
      )

    # Create user as inactive until OTP is verified
    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password),
        is_active=False,
    )

    # Generate 6-digit OTP and store in session
    otp = str(random.randint(100000, 999999))
    request.session['pending_user_id'] = user.id
    request.session['generated_otp'] = otp

    # Send OTP via SMTP
    send_mail(
        subject='Plexus Electro CRM - Email Verification OTP',
        message=f'Your email verification code is: {otp}',
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )

    return redirect('verify_otp')

  return render(request, 'main/register.html')


def verify_otp_view(request):
  if request.method == 'POST':
    entered_otp = request.POST.get('otp', '').strip()
    saved_otp = str(request.session.get('generated_otp', '')).strip()
    user_id = request.session.get('pending_user_id')

    if not saved_otp or not user_id:
      return render(
          request,
          'main/verify_otp.html',
          {'error': 'Session expired. Please register again.'},
      )

    if entered_otp == saved_otp:
      try:
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()

        # Clean up session data
        request.session.pop('pending_user_id', None)
        request.session.pop('generated_otp', None)

        return redirect('login')
      except User.DoesNotExist:
        return render(
            request, 'main/verify_otp.html', {'error': 'User not found.'}
        )
    else:
      return render(
          request,
          'main/verify_otp.html',
          {'error': 'Invalid OTP code. Please try again.'},
      )

  return render(request, 'main/verify_otp.html')


# ==========================================
# 2. LOGIN & DASHBOARD
# ==========================================


def login_view(request):
  if request.method == 'POST':
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()

    user = authenticate(request, username=username, password=password)
    if user is not None:
      if user.is_active:
        login(request, user)
        return redirect('dashboard')
      else:
        return render(
            request,
            'main/login.html',
            {'error': 'Account is not activated. Please complete verification.'},
        )
    else:
      return render(
          request,
          'main/login.html',
          {'error': 'Invalid username or password.'},
      )

  return render(request, 'main/login.html')


def dashboard_view(request):
  if not request.user.is_authenticated:
    return redirect('login')
  return render(request, 'main/dashboard.html', {'user': request.user})


def logout_view(request):
  logout(request)
  return redirect('login')


# ==========================================
# 3. PASSWORD RESET VIA OTP WORKFLOW
# ==========================================


def forgot_password_request_view(request):
  if request.method == 'POST':
    email = request.POST.get('email', '').strip()

    # Safely get the first user matching this email (prevents MultipleObjectsReturned error)
    user = User.objects.filter(email=email).first()

    if user:
      otp = str(random.randint(100000, 999999))

      request.session['reset_user_id'] = user.id
      request.session['reset_otp'] = otp

      send_mail(
          subject='Plexus Electro CRM - Password Reset OTP',
          message=f'Your password reset verification code is: {otp}',
          from_email=None,
          recipient_list=[user.email],
          fail_silently=False,
      )

      return redirect('verify_reset_otp')
    else:
      return render(
          request,
          'main/password_reset.html',
          {'error': 'No account found with this email address.'},
      )

  return render(request, 'main/password_reset.html')


def verify_reset_otp_view(request):
  if request.method == 'POST':
    entered_otp = request.POST.get('otp', '').strip()
    saved_otp = str(request.session.get('reset_otp', '')).strip()

    if not saved_otp or 'reset_user_id' not in request.session:
      return render(
          request,
          'main/verify_reset_otp.html',
          {'error': 'Session expired. Please request a new password reset.'},
      )

    if entered_otp == saved_otp:
      return redirect('reset_password_form')
    else:
      return render(
          request,
          'main/verify_reset_otp.html',
          {'error': 'Invalid OTP code. Please try again.'},
      )

  return render(request, 'main/verify_reset_otp.html')


def reset_password_form_view(request):
  user_id = request.session.get('reset_user_id')
  if not user_id:
    return redirect('forgot_password')

  if request.method == 'POST':
    new_password = request.POST.get('new_password', '').strip()
    confirm_password = request.POST.get('confirm_password', '').strip()

    if not new_password or len(new_password) < 6:
      return render(
          request,
          'main/password_reset_confirm.html',
          {'error': 'Password must be at least 6 characters long.'},
      )

    if new_password != confirm_password:
      return render(
          request,
          'main/password_reset_confirm.html',
          {'error': 'Passwords do not match.'},
      )

    try:
      user = User.objects.get(id=user_id)
      user.password = make_password(new_password)
      user.save()

      # Clear reset session variables
      request.session.pop('reset_user_id', None)
      request.session.pop('reset_otp', None)

      return redirect('login')
    except User.DoesNotExist:
      return render(
          request,
          'main/password_reset_confirm.html',
          {'error': 'User not found.'},
      )

  return render(request, 'main/password_reset_confirm.html')