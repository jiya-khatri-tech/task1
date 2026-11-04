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