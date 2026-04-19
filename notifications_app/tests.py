from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from campaigns.models import Campaign, Category
from .models import Notification

User = get_user_model()

class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='notifuser', role=User.Role.BACKER)
        self.creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        self.category = Category.objects.create(name='Tech')
        self.campaign = Campaign.objects.create(
            title='Notification Test',
            creator=self.creator,
            category=self.category
        )

    def test_create_notification(self):
        notification = Notification.objects.create(
            user=self.user,
            campaign=self.campaign,
            message='New pledge received',
            type=Notification.Type.PLEDGE
        )
        self.assertEqual(notification.message, 'New pledge received')
        self.assertEqual(notification.type, Notification.Type.PLEDGE)
        self.assertFalse(notification.is_read)
        self.assertEqual(str(notification), f'Notification for {self.user.username}: New pledge received')

    def test_mark_as_read(self):
        notification = Notification.objects.create(
            user=self.user,
            message='Test message'
        )
        notification.is_read = True
        notification.save()
        self.assertTrue(notification.is_read)

class NotificationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='notifuser', role=User.Role.BACKER)
        self.creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        self.category = Category.objects.create(name='Tech')
        self.campaign = Campaign.objects.create(
            title='API Notification Test',
            creator=self.creator,
            category=self.category
        )
        self.notification = Notification.objects.create(
            user=self.user,
            campaign=self.campaign,
            message='Test notification',
            type=Notification.Type.CAMPAIGN_UPDATE
        )

    def test_list_notifications(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_mark_notification_read(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('notification-detail', kwargs={'pk': self.notification.pk})
        data = {'is_read': True}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_list_notifications_unauthenticated(self):
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
