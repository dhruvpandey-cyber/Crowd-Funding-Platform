from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=User.Role.BACKER
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.role, User.Role.BACKER)

    def test_user_str(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(str(user), 'testuser')

    def test_user_is_creator(self):
        creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        backer = User.objects.create_user(username='backer', role=User.Role.BACKER)
        self.assertTrue(creator.is_creator)
        self.assertFalse(backer.is_creator)

    def test_user_is_backer(self):
        creator = User.objects.create_user(username='creator', role=User.Role.CREATOR)
        backer = User.objects.create_user(username='backer', role=User.Role.BACKER)
        self.assertFalse(creator.is_backer)
        self.assertTrue(backer.is_backer)

class RegisterViewTest(APITestCase):
    def test_register_backer(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'BACKER'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_creator(self):
        url = reverse('register')
        data = {
            'username': 'creatoruser',
            'email': 'creator@example.com',
            'password': 'creatorpass123',
            'role': 'CREATOR'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='creatoruser')
        self.assertEqual(user.role, User.Role.CREATOR)

    def test_register_duplicate_username(self):
        User.objects.create_user(username='existing', email='existing@example.com', password='pass')
        url = reverse('register')
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'newpass123',
            'role': 'BACKER'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ProfileViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='profilepass123',
            first_name='Profile',
            last_name='User'
        )

    def test_get_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')

    def test_get_profile_unauthenticated(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('profile')
        data = {'first_name': 'Updated', 'last_name': 'Name'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
