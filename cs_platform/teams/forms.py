from django import forms
from .models import Team, TeamMembership


class TeamCreateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'tag', 'logo', 'description', 'country']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tag': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_tag(self):
        tag = self.cleaned_data['tag']
        if not tag.isupper():
            raise forms.ValidationError("Team tag must be uppercase")
        return tag


class TeamJoinForm(forms.ModelForm):
    class Meta:
        model = TeamMembership
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }