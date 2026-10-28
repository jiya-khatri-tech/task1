from django.contrib.auth.models import User
from django.db import models


class Employee(models.Model):
  # Links to Django's built-in User model for authentication (login)
  user = models.OneToOneField(
      User, on_delete=models.CASCADE, null=True, blank=True
  )
  name = models.CharField(max_length=150)
  email = models.EmailField(unique=True)
  department = models.CharField(max_length=100, blank=True, null=True)
  role = models.CharField(max_length=100, blank=True, null=True)
  phone = models.CharField(max_length=15, blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.name} ({self.department})"