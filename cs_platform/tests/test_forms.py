from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.forms import CustomUserCreationForm, UserProfileForm
from teams.forms import TeamCreateForm, TeamJoinForm

User = get_user_model()

class FormsTest(TestCase):
    def test_user_creation_form_valid(self):
        """Test valid user creation form"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'country': 'Bulgaria'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_creation_form_invalid(self):
        """Test invalid user creation form"""
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'complexpass123',
            'password2': 'differentpass',
            'country': 'Bulgaria'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_team_creation_form_valid(self):
        """Test valid team creation form"""
        form_data = {
            'name': 'Test Team',
            'tag': 'TEST',
            'country': 'Bulgaria',
            'description': 'A test team'
        }
        form = TeamCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_team_creation_form_invalid_tag(self):
        """Test team creation form with invalid tag"""
        form_data = {
            'name': 'Test Team',
            'tag': 'test',  # Should be uppercase
            'country': 'Bulgaria',
            'description': 'A test team'
        }
        form = TeamCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_profile_form(self):
        """Test user profile form"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        form_data = {
            'bio': 'Updated bio',
            'country': 'Macedonia',
            'favorite_weapon': 'AK-47',
            'rank': 'legendary_eagle'
        }
        form = UserProfileForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())