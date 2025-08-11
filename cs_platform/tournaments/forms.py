from django import forms
from .models import Tournament, TournamentParticipation


class TournamentCreateForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'description', 'prize_pool', 'max_teams', 'start_date', 'end_date', 'registration_deadline',
                  'banner']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'prize_pool': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_teams': forms.NumberInput(attrs={'class': 'form-control', 'min': '2'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'registration_deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'banner': forms.FileInput(attrs={'class': 'form-control'}),
        }


class TournamentRegistrationForm(forms.Form):
    team = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select your team"
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from teams.models import Team
        self.fields['team'].queryset = Team.objects.filter(
            memberships__player=user,
            memberships__is_active=True
        ).distinct()