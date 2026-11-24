from django.contrib.auth.models import User
from django.db import models


class Employee(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=150)
  email = models.EmailField(unique=True)
  department = models.CharField(max_length=100, blank=True, null=True)
  role = models.CharField(
      max_length=100, blank=True, null=True
  )  # Selected role
  phone = models.CharField(max_length=20, blank=True, null=True)
  is_active = models.BooleanField(
      default=True
  )  # Status toggle for active/inactive
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.name


class Category(models.Model):
  name = models.CharField(max_length=150, unique=True)
  description = models.TextField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.name


class Product(models.Model):
  name = models.CharField(max_length=200)
  category = models.ForeignKey(
      Category, on_delete=models.CASCADE, related_name='products'
  )
  code = models.CharField(max_length=100, unique=True)
  hsn = models.CharField(
      max_length=50, verbose_name='HSN Code', blank=True, null=True
  )
  uom = models.CharField(max_length=50, verbose_name='UOM', default='NOS')
  sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
  price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  stock_quantity = models.PositiveIntegerField(default=0)
  description = models.TextField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f'{self.name} ({self.code})'


class Customer(models.Model):
  name = models.CharField(max_length=150)
  email = models.EmailField(unique=True)
  password = models.CharField(max_length=128)
  creator = models.ForeignKey(
      User,
      on_delete=models.CASCADE,
      related_name='created_customers',
  )
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.name