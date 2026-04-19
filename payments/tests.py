from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal

from campaigns.models import Campaign, Category
from pledges.models import Pledge
from .models import Payment

User = get_user_model()

class PaymentModelTest(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        self.backer = User.objects.create_user(username='backer', role=User.Role.BACKER)
        self.category = Category.objects.create(name='Tech')
        self.campaign = Campaign.objects.create(
            title='Payment Test',
            creator=self.creator,
            category=self.category,
            goal_amount=Decimal('1000.00')
        )
        self.pledge = Pledge.objects.create(
            backer=self.backer,
            campaign=self.campaign,
            amount=Decimal('50.00')
        )

    def test_create_payment(self):
        payment = Payment.objects.create(
            pledge=self.pledge,
            amount=Decimal('50.00'),
            gateway='sandbox',
            status=Payment.Status.COMPLETED
        )
        self.assertEqual(payment.amount, Decimal('50.00'))
        self.assertEqual(payment.status, Payment.Status.COMPLETED)
        self.assertEqual(str(payment), f'Payment for {self.pledge} - $50.00')

    def test_payment_status_choices(self):
        payment = Payment.objects.create(
            pledge=self.pledge,
            amount=Decimal('50.00'),
            gateway='sandbox'
        )
        self.assertEqual(payment.status, Payment.Status.PENDING)

class PaymentAPITest(APITestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        self.backer = User.objects.create_user(username='backer', role=User.Role.BACKER)
        self.category = Category.objects.create(name='Tech')
        self.campaign = Campaign.objects.create(
            title='API Payment Test',
            creator=self.creator,
            category=self.category,
            goal_amount=Decimal('1000.00')
        )
        self.pledge = Pledge.objects.create(
            backer=self.backer,
            campaign=self.campaign,
            amount=Decimal('50.00')
        )

    def test_list_payments_authenticated(self):
        self.client.force_authenticate(user=self.backer)
        url = reverse('payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_payment(self):
        self.client.force_authenticate(user=self.backer)
        url = reverse('payment-list')
        data = {
            'pledge': self.pledge.id,
            'amount': '50.00',
            'gateway': 'sandbox'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Payment.objects.filter(pledge=self.pledge).exists())

    def test_create_payment_unauthenticated(self):
        url = reverse('payment-list')
        data = {
            'pledge': self.pledge.id,
            'amount': '50.00',
            'gateway': 'sandbox'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
