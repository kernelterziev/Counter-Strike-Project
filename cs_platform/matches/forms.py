from django import forms
from .models import Match, PlayerMatchStats
from teams.models import Team


class MatchCreateForm(forms.ModelForm):
    # Enhanced team selection with both teams
    team1 = forms.ModelChoiceField(
        queryset=Team.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control team-selector',
            'id': 'team1Selector'
        }),
        label="Team 1 (Home Team)",
        help_text="Select the first team to compete"
    )

    team2 = forms.ModelChoiceField(
        queryset=Team.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control team-selector',
            'id': 'team2Selector'
        }),
        label="Team 2 (Away Team)",
        help_text="Select the opponent team"
    )

    class Meta:
        model = Match
        fields = ['team1', 'team2', 'map_name', 'match_type']
        widgets = {
            'map_name': forms.Select(attrs={
                'class': 'form-control map-selector',
                'id': 'mapSelector'
            }),
            'match_type': forms.Select(attrs={
                'class': 'form-control type-selector',
                'id': 'typeSelector'
            }),
        }
        labels = {
            'map_name': 'Battlefield Map',
            'match_type': 'Match Format',
        }
        help_texts = {
            'map_name': 'Choose the map for this epic battle',
            'match_type': 'Select the type of competition',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Enhanced team queryset with professional teams first
        teams_queryset = Team.objects.filter(is_active=True).order_by(
            '-is_professional', 'name'
        )

        self.fields['team1'].queryset = teams_queryset
        self.fields['team2'].queryset = teams_queryset

        # If user is provided, set their team as default for team1
        if user and user.is_authenticated:
            user_teams = Team.objects.filter(
                memberships__player=user,
                memberships__is_active=True,
                is_active=True
            ).distinct()

            if user_teams.exists():
                self.fields['team1'].initial = user_teams.first()

    def clean(self):
        cleaned_data = super().clean()
        team1 = cleaned_data.get('team1')
        team2 = cleaned_data.get('team2')

        if team1 and team2 and team1 == team2:
            raise forms.ValidationError(
                "A team cannot play against itself! Choose different teams."
            )

        return cleaned_data


class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team1_score', 'team2_score', 'duration_minutes', 'is_finished']
        widgets = {
            'team1_score': forms.NumberInput(attrs={
                'class': 'form-control score-input',
                'min': '0',
                'max': '30',
                'placeholder': 'Team 1 Score'
            }),
            'team2_score': forms.NumberInput(attrs={
                'class': 'form-control score-input',
                'min': '0',
                'max': '30',
                'placeholder': 'Team 2 Score'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control duration-input',
                'min': '1',
                'placeholder': 'Match Duration (minutes)'
            }),
            'is_finished': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'team1_score': 'Team 1 Final Score',
            'team2_score': 'Team 2 Final Score',
            'duration_minutes': 'Match Duration',
            'is_finished': 'Mark as Finished',
        }


class PlayerStatsForm(forms.ModelForm):
    class Meta:
        model = PlayerMatchStats
        fields = ['kills', 'deaths', 'assists', 'headshots', 'damage_dealt']
        widgets = {
            'kills': forms.NumberInput(attrs={
                'class': 'form-control stat-input',
                'min': '0',
                'placeholder': 'Kills'
            }),
            'deaths': forms.NumberInput(attrs={
                'class': 'form-control stat-input',
                'min': '0',
                'placeholder': 'Deaths'
            }),
            'assists': forms.NumberInput(attrs={
                'class': 'form-control stat-input',
                'min': '0',
                'placeholder': 'Assists'
            }),
            'headshots': forms.NumberInput(attrs={
                'class': 'form-control stat-input',
                'min': '0',
                'placeholder': 'Headshots'
            }),
            'damage_dealt': forms.NumberInput(attrs={
                'class': 'form-control stat-input',
                'min': '0',
                'placeholder': 'Damage Dealt'
            }),
        }