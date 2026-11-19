from django import forms
from .models import Category, Product


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