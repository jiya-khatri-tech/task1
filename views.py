import random
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm, CustomerForm, ProductForm
from .models import Category, Customer, Employee, Product


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
    identifier = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()

    # Agar user ne email dala hai, toh uske against actual username nikal lo
    username_to_auth = identifier
    if '@' in identifier:
      try:
        user_obj = User.objects.get(email=identifier)
        username_to_auth = user_obj.username
      except User.DoesNotExist:
        pass  # Agar email database mein nahi hai toh as-is pass karega

    # Ab authenticate karein (chahe username ho ya email)
    user = authenticate(request, username=username_to_auth, password=password)

    if user is not None:
      # Check if account is active
      if not user.is_active:
        messages.error(
            request,
            'Your account has been deactivated. Please contact the'
            ' administrator.',
        )
        return redirect('login')

      login(request, user)
      messages.success(
          request, f'Welcome back, {user.first_name or user.username}!'
      )
      return redirect('dashboard')
    else:
      messages.error(request, 'Invalid email/username or password.')

  return render(request, 'main/login.html')


def dashboard_view(request):
  if not request.user.is_authenticated:
    return redirect('login')
  return render(request, 'main/dashboard.html', {'user': request.user})


def customer_list_view(request):
  if not request.user.is_authenticated:
    return redirect('login')

  customers = Customer.objects.filter(creator=request.user).order_by(
      '-created_at', '-pk'
  )
  customers = Paginator(customers, 10).get_page(request.GET.get('page'))
  return render(
      request,
      'main/customer_list.html',
      {
          'customers': customers,
          'page_range': customers.paginator.get_elided_page_range(
              number=customers.number
          ),
      },
  )


def add_customer_view(request):
  if not request.user.is_authenticated:
    return redirect('login')

  if request.method == 'POST':
    form = CustomerForm(request.POST)
    if form.is_valid():
      customer = form.save(commit=False)
      customer.creator = request.user
      customer.password = make_password(form.cleaned_data['password'])
      customer.save()
      messages.success(request, f'Customer "{customer.name}" registered successfully!')
      return redirect('customer_list')
  else:
    form = CustomerForm()

  return render(request, 'main/add_customer.html', {'form': form})


def edit_customer_view(request, pk):
  if not request.user.is_authenticated:
    return redirect('login')

  customer = get_object_or_404(Customer, pk=pk, creator=request.user)
  if request.method == 'POST':
    form = CustomerForm(request.POST, instance=customer)
    if form.is_valid():
      customer = form.save(commit=False)
      password = form.cleaned_data.get('password')
      if password:
        customer.password = make_password(password)
      customer.save()
      messages.success(request, f'Customer "{customer.name}" updated successfully!')
      return redirect('customer_list')
  else:
    form = CustomerForm(instance=customer)

  return render(
      request,
      'main/edit_customer.html',
      {'form': form, 'customer': customer},
  )


def delete_customer_view(request, pk):
  if not request.user.is_authenticated:
    return redirect('login')

  customer = get_object_or_404(Customer, pk=pk, creator=request.user)
  if request.method == 'POST':
    customer_name = customer.name
    customer.delete()
    messages.success(request, f'Customer "{customer_name}" deleted successfully!')
    return redirect('customer_list')

  return render(
      request,
      'main/delete_customer_confirm.html',
      {'customer': customer},
  )


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

      # 1. Update password securely in the database (hashed)
      user.password = make_password(new_password)
      user.save()

      # 2. Notify the user via email that their password was changed
      send_mail(
          subject='Plexus Electro CRM - Password Successfully Updated',
          message=(
              f'Hello {user.username},\n\nYour password for Plexus Electro CRM'
              ' has been successfully updated.\n\nIf you did not make this'
              ' change, please contact support immediately.'
          ),
          from_email=None,
          recipient_list=[user.email],
          fail_silently=False,
      )

      # 3. Clear reset session variables for security
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


# ==========================================
# 4. EMPLOYEE MANAGEMENT
# ==========================================


def admin_register_employee_view(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  if request.method == 'POST':
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()
    department = request.POST.get('department', '').strip()
    role = request.POST.get(
        'role', ''
    ).strip()  # Capture selected role from registration form
    phone = request.POST.get('phone', '').strip()
    # Checkbox returns 'on' if checked, else None/False
    is_active = True if request.POST.get('is_active') == 'on' else False

    if User.objects.filter(email=email).exists():
      messages.error(request, 'An account with this email already exists.')
      return render(request, 'main/admin_register_employee.html')

    try:
      # 1. Create Login User account
      user = User.objects.create_user(
          username=email, email=email, password=password, is_active=is_active
      )
      user.first_name = name
      user.save()

      # 2. Create Employee profile instance with the selected role and active status
      Employee.objects.create(
          user=user,
          name=name,
          email=email,
          department=department,
          role=role,
          phone=phone,
          is_active=is_active,
      )

      messages.success(request, f'Employee "{name}" registered successfully!')
      return redirect('employee_list')
    except Exception as e:
      messages.error(request, f'Error creating employee: {str(e)}')
      return render(request, 'main/admin_register_employee.html')

  return render(request, 'main/admin_register_employee.html')


def edit_employee_view(request, employee_id):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  try:
    employee = Employee.objects.get(id=employee_id)
  except Employee.DoesNotExist:
    messages.error(request, 'Employee record not found.')
    return redirect('employee_list')

  if request.method == 'POST':
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    department = request.POST.get('department', '').strip()
    role = request.POST.get('role', '').strip()  # Updated role instance
    phone = request.POST.get('phone', '').strip()
    is_active = True if request.POST.get('is_active') == 'on' else False

    try:
      # Update employee model instance fields
      employee.name = name
      employee.email = email
      employee.department = department
      employee.role = role  # Update selected role
      employee.phone = phone
      employee.is_active = is_active
      employee.save()

      # Sync active status and details with associated User account
      if employee.user:
        user = employee.user
        user.email = email
        user.first_name = name
        user.is_active = is_active
        user.save()

      messages.success(request, f'Employee "{name}" updated successfully!')
      return redirect('employee_list')
    except Exception as e:
      messages.error(request, f'Error updating employee: {str(e)}')

  return render(request, 'main/edit_employee.html', {'employee': employee})


def delete_employee_view(request, employee_id):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  try:
    employee = Employee.objects.get(id=employee_id)
  except Employee.DoesNotExist:
    messages.error(request, 'Employee record not found.')
    return redirect('employee_list')

  if request.method == 'POST':
    emp_name = employee.name
    if employee.user:
      employee.user.delete()  # Cascades deletion to Employee profile
    else:
      employee.delete()

    # Display success message after deletion
    messages.success(
        request, f'Employee "{emp_name}" has been deleted successfully.'
    )
    return redirect('employee_list')

  return render(
      request, 'main/delete_employee_confirm.html', {'employee': employee}
  )


def employee_list_view(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  employees = Employee.objects.all().order_by('-created_at')
  return render(request, 'main/employee_list.html', {'employees': employees})


# ==========================================
# 5. INVENTORY: CATEGORIES & PRODUCTS
# ==========================================


def add_category_view(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  if request.method == 'POST':
    form = CategoryForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request, 'New product category created successfully!')
      return redirect('category_list')
    else:
      messages.error(request, 'Please correct the errors below.')
  else:
    form = CategoryForm()

  return render(request, 'main/add_category.html', {'form': form})


def add_product_view(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  if request.method == 'POST':
    form = ProductForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request, 'New product added to inventory successfully!')
      return redirect('product_list')
    else:
      messages.error(request, 'Please correct the errors below.')
  else:
    form = ProductForm()

  return render(request, 'main/add_product.html', {'form': form})


def category_list_view(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  categories = Category.objects.all().order_by('-created_at')
  return render(request, 'main/category_list.html', {'categories': categories})


def edit_category_view(request, pk):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  category = get_object_or_404(Category, pk=pk)

  if request.method == 'POST':
    form = CategoryForm(request.POST, instance=category)
    if form.is_valid():
      form.save()
      messages.success(request, 'Category updated successfully!')
      return redirect('category_list')
    else:
      messages.error(request, 'Please correct the errors below.')
  else:
    form = CategoryForm(instance=category)

  return render(
      request, 'main/edit_category.html', {'form': form, 'category': category}
  )


def delete_category_view(request, pk):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  category = get_object_or_404(Category, pk=pk)

  if request.method == 'POST':
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('category_list')

  return render(
      request, 'main/delete_category_confirm.html', {'category': category}
  )


def product_list_view(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  query = request.GET.get('q', '').strip()
  products = (
      Product.objects.all().select_related('category').order_by('-created_at')
  )

  if query:
    products = products.filter(
        Q(name__icontains=query) | Q(category__name__icontains=query)
    )

  return render(
      request,
      'main/product_list.html',
      {
          'products': products,
          'search_query': query,
      },
  )


def edit_product_view(request, pk):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  product = get_object_or_404(Product, pk=pk)

  if request.method == 'POST':
    form = ProductForm(request.POST, instance=product)
    if form.is_valid():
      form.save()
      messages.success(request, 'Product updated successfully!')
      return redirect('product_list')
    else:
      messages.error(request, 'Please correct the errors below.')
  else:
    form = ProductForm(instance=product)

  return render(
      request, 'main/edit_product.html', {'form': form, 'product': product}
  )


def delete_product_view(request, pk):
  if not request.user.is_authenticated or not request.user.is_staff:
    messages.error(request, 'Access denied. Administrator privileges required.')
    return redirect('login')

  product = get_object_or_404(Product, pk=pk)

  if request.method == 'POST':
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('product_list')

  return render(
      request, 'main/delete_product_confirm.html', {'product': product}
  )