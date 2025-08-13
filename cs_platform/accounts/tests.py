from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from teams.models import Team, TeamMembership
from matches.models import Match
import json

User = get_user_model()


class UserRegistrationTestCase(TestCase):
    """Test user registration functionality"""

    def setUp(self):
        self.client = Client()

    def test_user_can_register(self):
        """Test that users can successfully register"""
        response = self.client.post(reverse('register'), {
            'username': 'testplayer',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'email': 'test@test.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='testplayer').exists())

    def test_duplicate_username_fails(self):
        """Test that duplicate usernames are rejected"""
        User.objects.create_user('existinguser', 'exist@test.com', 'pass123')
        response = self.client.post(reverse('register'), {
            'username': 'existinguser',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'email': 'new@test.com'
        })
        self.assertEqual(response.status_code, 200)  # Stay on page
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)


class UserAuthenticationTestCase(TestCase):
    """Test authentication functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
        )

    def test_user_can_login(self):
        """Test that users can login with correct credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_wrong_password_fails(self):
        """Test that wrong password prevents login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)

    def test_user_can_logout(self):
        """Test that logged in users can logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class ProfileTestCase(TestCase):
    """Test user profile functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='profileuser',
            password='pass123',
            rank='gold_nova_1',
            hours_played=100
        )

    def test_profile_displays_correctly(self):
        """Test that user profile shows correct information"""
        response = self.client.get(reverse('player_detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profileuser')

    def test_profile_edit_requires_login(self):
        """Test that profile editing requires authentication"""
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 302)