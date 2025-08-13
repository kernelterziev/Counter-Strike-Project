from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from teams.models import Team, TeamMembership
from matches.models import Match
import json

User = get_user_model()


class APITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='testpass123',
            country='Bulgaria',
            rank='global_elite'
        )
        self.team = Team.objects.create(
            name='API Team',
            tag='API',
            country='Bulgaria',
            captain=self.user
        )

    def test_api_overview(self):
        """Test API overview endpoint"""
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('API Overview', response.data)
        self.assertIn('Players', response.data)
        self.assertIn('Teams', response.data)

    def test_players_api_endpoint(self):
        """Test players API endpoint"""
        response = self.client.get('/api/players/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_player_detail_api_endpoint(self):
        """Test player detail API endpoint"""
        response = self.client.get(f'/api/players/{self.user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'apiuser')
        self.assertEqual(response.data['country'], 'Bulgaria')

    def test_teams_api_endpoint(self):
        """Test teams API endpoint"""
        response = self.client.get('/api/teams/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_team_detail_api_endpoint(self):
        """Test team detail API endpoint"""
        response = self.client.get(f'/api/teams/{self.team.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'API Team')
        self.assertEqual(response.data['tag'], 'API')

    def test_professional_players_filter(self):
        """Test professional players filter"""
        # Create professional player
        pro_user = User.objects.create_user(
            username='prozywoo',
            email='pro@example.com',
            password='testpass123',
            is_professional=True,
            real_name='Test Pro'
        )

        response = self.client.get('/api/players/?is_professional=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that only professional players are returned
        for player in response.data['results']:
            self.assertTrue(player['is_professional'])

    def test_professional_teams_filter(self):
        """Test professional teams filter"""
        # Create professional team
        pro_team = Team.objects.create(
            name='Pro Team',
            tag='PRO',
            country='France',
            is_professional=True,
            world_ranking=1,
            captain=self.user
        )

        response = self.client.get('/api/teams/?is_professional=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that only professional teams are returned
        for team in response.data['results']:
            self.assertTrue(team['is_professional'])