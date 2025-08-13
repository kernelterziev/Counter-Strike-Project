from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from teams.models import Team, TeamMembership
from matches.models import Match, PlayerMatchStats
from tournaments.models import Tournament, TournamentParticipation
from datetime import date, datetime
from django.utils import timezone

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testplayer',
            email='test@example.com',
            password='testpass123',
            country='Bulgaria',
            rank='global_elite',
            hours_played=1500
        )

    def test_user_creation(self):
        """Test user model creation"""
        self.assertEqual(self.user.username, 'testplayer')
        self.assertEqual(self.user.country, 'Bulgaria')
        self.assertEqual(self.user.rank, 'global_elite')
        self.assertEqual(self.user.hours_played, 1500)
        self.assertFalse(self.user.is_professional)

    def test_user_string_representation(self):
        """Test user __str__ method"""
        expected = "testplayer (global_elite)"
        self.assertEqual(str(self.user), expected)

    def test_country_flag_method(self):
        """Test get_country_flag method"""
        flag = self.user.get_country_flag()
        self.assertEqual(flag, '🇧🇬')

    def test_professional_user_creation(self):
        """Test professional user creation"""
        pro_user = User.objects.create_user(
            username='ZywOo',
            email='zywoo@vitality.gg',
            password='propass123',
            country='France',
            rank='global_elite',
            is_professional=True,
            real_name='Mathieu Herbaut',
            hltv_rating=7.2
        )
        self.assertTrue(pro_user.is_professional)
        self.assertEqual(pro_user.real_name, 'Mathieu Herbaut')
        self.assertEqual(pro_user.hltv_rating, 7.2)

class TeamModelTest(TestCase):
    def setUp(self):
        self.captain = User.objects.create_user(
            username='captain',
            email='captain@example.com',
            password='testpass123'
        )
        self.team = Team.objects.create(
            name='Test Team',
            tag='TEST',
            country='Bulgaria',
            captain=self.captain,
            description='A test team'
        )

    def test_team_creation(self):
        """Test team model creation"""
        self.assertEqual(self.team.name, 'Test Team')
        self.assertEqual(self.team.tag, 'TEST')
        self.assertEqual(self.team.country, 'Bulgaria')
        self.assertEqual(self.team.captain, self.captain)
        self.assertTrue(self.team.is_active)

    def test_team_string_representation(self):
        """Test team __str__ method"""
        expected = "[TEST] Test Team"
        self.assertEqual(str(self.team), expected)

    def test_professional_team_creation(self):
        """Test professional team creation"""
        pro_team = Team.objects.create(
            name='Vitality',
            tag='VIT',
            country='France',
            is_professional=True,
            world_ranking=1,
            prize_money=1205000,
            captain=self.captain
        )
        self.assertTrue(pro_team.is_professional)
        self.assertEqual(pro_team.world_ranking, 1)
        self.assertEqual(pro_team.prize_money, 1205000)

class TeamMembershipTest(TestCase):
    def setUp(self):
        self.player = User.objects.create_user(
            username='player1',
            email='player1@example.com',
            password='testpass123'
        )
        self.team = Team.objects.create(
            name='Test Team',
            tag='TEST',
            country='Bulgaria',
            captain=self.player
        )

    def test_team_membership_creation(self):
        """Test team membership creation"""
        membership = TeamMembership.objects.create(
            team=self.team,
            player=self.player,
            role='rifler'
        )
        self.assertEqual(membership.team, self.team)
        self.assertEqual(membership.player, self.player)
        self.assertEqual(membership.role, 'rifler')
        self.assertTrue(membership.is_active)

    def test_unique_team_player_constraint(self):
        """Test that a player can't join the same team twice"""
        TeamMembership.objects.create(
            team=self.team,
            player=self.player,
            role='rifler'
        )
        # This should raise an integrity error
        with self.assertRaises(Exception):
            TeamMembership.objects.create(
                team=self.team,
                player=self.player,
                role='awper'
            )