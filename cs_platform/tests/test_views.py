from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from teams.models import Team, TeamMembership
from matches.models import Match
from tournaments.models import Tournament

User = get_user_model()

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.team = Team.objects.create(
            name='Test Team',
            tag='TEST',
            country='Bulgaria',
            captain=self.user
        )

    def test_home_page_view(self):
        """Test home page loads correctly"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CS Platform')

    def test_player_list_view(self):
        """Test player list view"""
        response = self.client.get(reverse('player_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Players')

    def test_player_detail_view(self):
        """Test player detail view"""
        response = self.client.get(reverse('player_detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_team_list_view(self):
        """Test team list view"""
        response = self.client.get(reverse('team_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Teams')

    def test_team_detail_view(self):
        """Test team detail view"""
        response = self.client.get(reverse('team_detail', kwargs={'pk': self.team.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.team.name)

    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'country': 'Macedonia'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_required_views(self):
        """Test that protected views require login"""
        response = self.client.get(reverse('team_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_team_creation_with_login(self):
        """Test team creation for logged in user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('team_create'), {
            'name': 'New Team',
            'tag': 'NEW',
            'country': 'Serbia',
            'description': 'A new team'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Team.objects.filter(name='New Team').exists())