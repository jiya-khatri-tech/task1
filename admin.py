from django.contrib import admin
from .models import Category, Customer, Employee, Product

# Register your Employee model here so it appears in the admin panel
admin.site.register(Employee)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)