from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Customer, Product


class CustomerTests(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(
        username='creator',
        email='creator@example.com',
        password='StrongPass123!',
    )
    self.client.login(username='creator', password='StrongPass123!')

  def test_add_customer_links_creator_and_hashes_password(self):
    response = self.client.post(
        reverse('add_customer'),
        {
            'name': 'Test Customer',
            'email': 'customer@example.com',
            'password': 'CustomerPass123!',
            'confirm_password': 'CustomerPass123!',
        },
    )

    self.assertRedirects(response, reverse('customer_list'))
    customer = Customer.objects.get(email='customer@example.com')
    self.assertEqual(customer.creator, self.user)
    self.assertTrue(check_password('CustomerPass123!', customer.password))

  def test_customer_is_private_to_creator(self):
    Customer.objects.create(
        name='Private Customer',
        email='private@example.com',
        password='hashed-password',
        creator=self.user,
    )
    other_user = User.objects.create_user(
        username='other',
        email='other@example.com',
        password='StrongPass123!',
    )
    self.client.logout()
    self.client.login(username='other', password='StrongPass123!')

    response = self.client.get(reverse('customer_list'))

    self.assertNotContains(response, 'Private Customer')


class ProductCategoryUpdateTests(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(
        username='inventory-admin',
        password='StrongPass123!',
        is_staff=True,
    )
    self.client.login(username='inventory-admin', password='StrongPass123!')
    self.category = Category.objects.create(name='Electronics')
    self.other_category = Category.objects.create(name='Components')
    self.product = Product.objects.create(
        name='Power Supply',
        category=self.category,
        code='PS-001',
        uom='NOS',
        sku='PS-SKU-001',
        price='199.99',
        stock_quantity=10,
    )

  def test_product_category_relationship_updates(self):
    response = self.client.post(
        reverse('edit_product', args=[self.product.pk]),
        {
            'name': self.product.name,
            'category': self.other_category.pk,
            'code': self.product.code,
            'hsn': '',
            'uom': self.product.uom,
            'sku': self.product.sku,
            'price': '199.99',
            'stock_quantity': 10,
            'description': '',
        },
    )

    self.assertRedirects(response, reverse('product_list'))
    self.product.refresh_from_db()
    self.assertEqual(self.product.category, self.other_category)
    self.assertIn(self.product, self.other_category.products.all())
