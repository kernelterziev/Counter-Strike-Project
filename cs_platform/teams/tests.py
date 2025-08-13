from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from teams.models import Team, TeamMembership

User = get_user_model()


class TeamCreationTestCase(TestCase):
    """Test team creation functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('teamowner', 'owner@test.com', 'pass123')
        self.client.login(username='teamowner', password='pass123')

    def test_authenticated_user_can_create_team(self):
        """Test that logged in users can create teams"""
        response = self.client.post(reverse('team_create'), {
            'name': 'Test Team',
            'tag': 'TT',
            'country': 'Bulgaria',
            'description': 'Test team description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Team.objects.filter(name='Test Team').exists())

    def test_team_creator_becomes_captain(self):
        """Test that team creator automatically becomes captain"""
        self.client.post(reverse('team_create'), {
            'name': 'Captain Test',
            'tag': 'CT',
            'country': 'Macedonia',
            'description': 'Testing captain assignment'
        })
        team = Team.objects.get(name='Captain Test')
        self.assertEqual(team.captain, self.user)

    def test_anonymous_cannot_create_team(self):
        """Test that anonymous users cannot create teams"""
        self.client.logout()
        response = self.client.post(reverse('team_create'), {
            'name': 'Should Fail',
            'tag': 'SF',
            'country': 'Serbia',
            'description': 'This should not work'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertFalse(Team.objects.filter(name='Should Fail').exists())


class TeamMembershipTestCase(TestCase):
    """Test team membership functionality"""

    def setUp(self):
        self.client = Client()
        self.captain = User.objects.create_user('captain', 'cap@test.com', 'pass123')
        self.player = User.objects.create_user('player1', 'p1@test.com', 'pass123')
        self.team = Team.objects.create(
            name='Test Squad',
            tag='TS',
            captain=self.captain,
            country='Greece'
        )

    def test_player_can_join_team(self):
        """Test that players can join teams"""
        self.client.login(username='player1', password='pass123')
        response = self.client.post(reverse('join_team', kwargs={'pk': self.team.pk}), {
            'role': 'rifler',
        })
        self.assertTrue(
            TeamMembership.objects.filter(team=self.team, player=self.player).exists()
        )

    def test_captain_cannot_join_own_team(self):
        """Test that captain cannot join their own team as member"""
        self.client.login(username='captain', password='pass123')
        initial_count = TeamMembership.objects.filter(team=self.team).count()
        response = self.client.post(reverse('join_team', kwargs={'pk': self.team.pk}))
        final_count = TeamMembership.objects.filter(team=self.team).count()
        self.assertEqual(initial_count, final_count)