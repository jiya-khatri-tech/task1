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
        'sku': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'e.g. ELEC-SKU-001'}
        ),
        'price': forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': '0.00'}
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