from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from .models import Campaign, Category, RewardTier

User = get_user_model()

class CategoryModelTest(TestCase):
    def test_create_category(self):
        category = Category.objects.create(name='Test Category', description='Test Desc')
        self.assertEqual(category.name, 'Test Category')
        self.assertEqual(str(category), 'Test Category')

class CampaignModelTest(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        self.category = Category.objects.create(name='Tech', description='Technology')

    def test_create_campaign(self):
        campaign = Campaign.objects.create(
            title='Test Campaign',
            creator=self.creator,
            category=self.category,
            short_description='Short desc',
            story='Long story',
            goal_amount=Decimal('1000.00'),
            min_pledge_amount=Decimal('10.00'),
            deadline=timezone.now() + timedelta(days=30)
        )
        self.assertEqual(campaign.title, 'Test Campaign')
        self.assertEqual(campaign.status, Campaign.Status.DRAFT)
        self.assertEqual(str(campaign), 'Test Campaign')

    def test_campaign_is_active(self):
        active_campaign = Campaign.objects.create(
            title='Active',
            creator=self.creator,
            category=self.category,
            status=Campaign.Status.ACTIVE,
            deadline=timezone.now() + timedelta(days=1)
        )
        expired_campaign = Campaign.objects.create(
            title='Expired',
            creator=self.creator,
            category=self.category,
            status=Campaign.Status.ACTIVE,
            deadline=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(active_campaign.is_active)
        self.assertFalse(expired_campaign.is_active)

    def test_campaign_progress(self):
        campaign = Campaign.objects.create(
            title='Progress Test',
            creator=self.creator,
            category=self.category,
            goal_amount=Decimal('100.00')
        )
        # Assuming total_raised is calculated via pledges
        self.assertEqual(campaign.progress_percent, 0)

class RewardTierModelTest(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        self.category = Category.objects.create(name='Tech')
        self.campaign = Campaign.objects.create(
            title='Campaign',
            creator=self.creator,
            category=self.category,
            goal_amount=Decimal('1000.00')
        )

    def test_create_reward_tier(self):
        reward = RewardTier.objects.create(
            campaign=self.campaign,
            title='Early Bird',
            description='Early supporter',
            amount=Decimal('50.00')
        )
        self.assertEqual(reward.title, 'Early Bird')
        self.assertEqual(str(reward), 'Early Bird - $50.00')

class CampaignAPITest(APITestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        self.category = Category.objects.create(name='Tech')
        self.campaign = Campaign.objects.create(
            title='API Test Campaign',
            creator=self.creator,
            category=self.category,
            short_description='API test',
            story='API story',
            goal_amount=Decimal('1000.00'),
            min_pledge_amount=Decimal('10.00'),
            deadline=timezone.now() + timedelta(days=30),
            status=Campaign.Status.ACTIVE
        )

    def test_list_campaigns(self):
        url = reverse('campaign-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_retrieve_campaign(self):
        url = reverse('campaign-detail', kwargs={'pk': self.campaign.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Test Campaign')

    def test_create_campaign_authenticated_creator(self):
        self.client.force_authenticate(user=self.creator)
        url = reverse('campaign-list')
        data = {
            'title': 'New Campaign',
            'category': self.category.id,
            'short_description': 'New desc',
            'story': 'New story',
            'goal_amount': '500.00',
            'min_pledge_amount': '5.00',
            'deadline': (timezone.now() + timedelta(days=30)).isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_campaign_unauthenticated(self):
        url = reverse('campaign-list')
        data = {
            'title': 'New Campaign',
            'category': self.category.id,
            'short_description': 'New desc',
            'story': 'New story',
            'goal_amount': '500.00',
            'min_pledge_amount': '5.00',
            'deadline': (timezone.now() + timedelta(days=30)).isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
