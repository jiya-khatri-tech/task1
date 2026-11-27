from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Category, Customer, Product


class CategoryForm(forms.ModelForm):

  class Meta:
    model = Category
    fields = ['name', 'description']
    widgets = {
        'name': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter category name'}
        ),
        'description': forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description (optional)',
            }
        ),
    }


class ProductForm(forms.ModelForm):

  class Meta:
    model = Product
    fields = [
        'name',
        'category',
        'code',
        'hsn',
        'uom',
        'sku',
        'price',
        'stock_quantity',
        'description',
    ]
    widgets = {
        'name': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter product name'}
        ),
        'category': forms.Select(attrs={'class': 'form-select'}),
        'code': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'e.g. PRD-001'}
        ),
        'hsn': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'e.g. 8504'}
        ),
        'uom': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'e.g. NOS, PCS, KG'}
        ),
        'sku': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'e.g. ELEC-SKU-001'}
        ),
        'price': forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }
        ),
        'stock_quantity': forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': '0'}
        ),
        'description': forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter product details...',
            }
        ),
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['category'].queryset = Category.objects.all().order_by('name')
    self.fields['category'].empty_label = '-- Select Category --'


class CustomerForm(forms.ModelForm):
  password = forms.CharField(
      required=False,
      widget=forms.PasswordInput(
          attrs={
              'class': 'form-control',
              'placeholder': 'Enter a secure password',
          }
      ),
      help_text='Leave blank to keep the existing password.',
  )
  confirm_password = forms.CharField(
      required=False,
      widget=forms.PasswordInput(
          attrs={
              'class': 'form-control',
              'placeholder': 'Confirm password',
          }
      ),
  )

  class Meta:
    model = Customer
    fields = ['name', 'email', 'is_active']
    widgets = {
        'name': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter customer name'}
        ),
        'email': forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'customer@example.com'}
        ),
        'is_active': forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        ),
    }

  def clean_email(self):
    email = self.cleaned_data['email'].strip().lower()
    customers = Customer.objects.filter(email=email)
    if self.instance.pk:
      customers = customers.exclude(pk=self.instance.pk)
    if customers.exists():
      raise forms.ValidationError('A customer with this email already exists.')
    return email

  def clean(self):
    cleaned_data = super().clean()
    password = cleaned_data.get('password', '')
    confirm_password = cleaned_data.get('confirm_password', '')

    if password or confirm_password:
      if password != confirm_password:
        self.add_error('confirm_password', 'Passwords do not match.')
      else:
        try:
          validate_password(password)
        except ValidationError as error:
          self.add_error('password', error)
    elif not self.instance.pk:
      self.add_error('password', 'Password is required.')
    return cleaned_data