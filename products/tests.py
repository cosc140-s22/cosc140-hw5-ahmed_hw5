from django.test import TestCase, Client
from django.test.utils import setup_test_environment, teardown_test_environment
from django.urls import reverse

from .models import Product

class ProductModelTests(TestCase):
    def test_age_range(self):
        p = Product(name="test", price=1.0, minimum_age_appropriate=0)
        self.assertEqual(p.age_range(), "Ages 0 and up")

        p = Product(name="test", price=1.0, minimum_age_appropriate=0, maximum_age_appropriate=2)
        self.assertEqual(p.age_range(), "Ages 0 to 2")

        p = Product(name="test", price=1.0, minimum_age_appropriate=2, maximum_age_appropriate=2)
        self.assertEqual(p.age_range(), "Age 2")

class ProductViewTests(TestCase):
    def test_index(self):
        Product.objects.create(name="test", description="test toy", price=11.99, minimum_age_appropriate=1)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ages 1 and up")
        self.assertContains(response, "11.99")

    def test_show(self):
        Product.objects.create(name="test", description="this is a complete test toy description", price=11.99, minimum_age_appropriate=1)
        response = self.client.get('/products/1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "this is a complete test toy description")

    def test_show_404(self):
        response = self.client.get('/products/100')
        self.assertEqual(response.status_code, 404)

    def test_root(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/products/')
