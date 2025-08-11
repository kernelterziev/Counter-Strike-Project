from django import forms
from .models import Match, PlayerMatchStats

class MatchCreateForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team2', 'map_name', 'match_type']
        widgets = {
            'team2': forms.Select(attrs={'class': 'form-control'}),
            'map_name': forms.Select(attrs={'class': 'form-control'}),
            'match_type': forms.Select(attrs={'class': 'form-control'}),
        }

class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team1_score', 'team2_score', 'duration_minutes', 'is_finished']
        widgets = {
            'team1_score': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '30'}),
            'team2_score': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '30'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'is_finished': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PlayerStatsForm(forms.ModelForm):
    class Meta:
        model = PlayerMatchStats
        fields = ['kills', 'deaths', 'assists', 'headshots', 'damage_dealt']
        widgets = {
            'kills': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'deaths': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'assists': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'headshots': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'damage_dealt': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }