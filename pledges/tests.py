from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from campaigns.models import Campaign, Category
from .models import Pledge

User = get_user_model()

class PledgeModelTest(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        self.backer = User.objects.create_user(username='backer', role=User.Role.BACKER)
        self.category = Category.objects.create(name='Tech')
        self.campaign = Campaign.objects.create(
            title='Pledge Test',
            creator=self.creator,
            category=self.category,
            goal_amount=Decimal('1000.00'),
            min_pledge_amount=Decimal('10.00'),
            deadline=timezone.now() + timedelta(days=30),
            status=Campaign.Status.ACTIVE
        )

    def test_create_pledge(self):
        pledge = Pledge.objects.create(
            backer=self.backer,
            campaign=self.campaign,
            amount=Decimal('50.00')
        )
        self.assertEqual(pledge.amount, Decimal('50.00'))
        self.assertEqual(str(pledge), f'Pledge by {self.backer.username} to {self.campaign.title}')

    def test_pledge_amount_validation(self):
        # Test minimum pledge
        pledge = Pledge(
            backer=self.backer,
            campaign=self.campaign,
            amount=Decimal('5.00')  # Below min
        )
        with self.assertRaises(Exception):  # Assuming model validation
            pledge.full_clean()

class PledgeAPITest(APITestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        self.backer = User.objects.create_user(username='backer', role=User.Role.BACKER)
        self.category = Category.objects.create(name='Tech')
        self.campaign = Campaign.objects.create(
            title='API Pledge Test',
            creator=self.creator,
            category=self.category,
            goal_amount=Decimal('1000.00'),
            min_pledge_amount=Decimal('10.00'),
            deadline=timezone.now() + timedelta(days=30),
            status=Campaign.Status.ACTIVE
        )

    def test_list_pledges_authenticated(self):
        self.client.force_authenticate(user=self.backer)
        url = reverse('pledge-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_pledge(self):
        self.client.force_authenticate(user=self.backer)
        url = reverse('pledge-list')
        data = {
            'campaign': self.campaign.id,
            'amount': '50.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Pledge.objects.filter(backer=self.backer, campaign=self.campaign).exists())

    def test_create_pledge_unauthenticated(self):
        url = reverse('pledge-list')
        data = {
            'campaign': self.campaign.id,
            'amount': '50.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_pledge_below_minimum(self):
        self.client.force_authenticate(user=self.backer)
        url = reverse('pledge-list')
        data = {
            'campaign': self.campaign.id,
            'amount': '5.00'  # Below min
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
