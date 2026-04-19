from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from campaigns.models import Campaign, Category
from .models import Report

User = get_user_model()

class ReportModelTest(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        self.reporter = User.objects.create_user(username='reporter', role=User.Role.BACKER)
        self.category = Category.objects.create(name='Tech')
        self.campaign = Campaign.objects.create(
            title='Report Test',
            creator=self.creator,
            category=self.category
        )

    def test_create_report(self):
        report = Report.objects.create(
            campaign=self.campaign,
            reporter=self.reporter,
            reason=Report.Reason.SPAM,
            description='This is spam'
        )
        self.assertEqual(report.reason, Report.Reason.SPAM)
        self.assertEqual(report.status, Report.Status.PENDING)
        self.assertEqual(str(report), f'Report on {self.campaign.title} by {self.reporter.username}')

    def test_report_status_update(self):
        report = Report.objects.create(
            campaign=self.campaign,
            reporter=self.reporter,
            reason=Report.Reason.SPAM
        )
        report.status = Report.Status.RESOLVED
        report.save()
        self.assertEqual(report.status, Report.Status.RESOLVED)

class ReportAPITest(APITestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        self.reporter = User.objects.create_user(username='reporter', role=User.Role.BACKER)
        self.category = Category.objects.create(name='Tech')
        self.campaign = Campaign.objects.create(
            title='API Report Test',
            creator=self.creator,
            category=self.category
        )

    def test_list_reports_authenticated(self):
        self.client.force_authenticate(user=self.creator)
        url = reverse('report-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_report(self):
        self.client.force_authenticate(user=self.reporter)
        url = reverse('report-list')
        data = {
            'campaign': self.campaign.id,
            'reason': 'SPAM',
            'description': 'Spam campaign'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Report.objects.filter(campaign=self.campaign, reporter=self.reporter).exists())

    def test_create_report_unauthenticated(self):
        url = reverse('report-list')
        data = {
            'campaign': self.campaign.id,
            'reason': 'SPAM',
            'description': 'Spam campaign'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
