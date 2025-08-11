from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone

User = get_user_model()


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tag = models.CharField(max_length=10, unique=True)  # Team tag like [NAVI]
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)
    founded_date = models.DateField(default=timezone.now)
    description = models.TextField(max_length=1000, blank=True)
    country = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    captain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='captained_teams')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"[{self.tag}] {self.name}"


class TeamMembership(models.Model):
    ROLE_CHOICES = [
        ('rifler', 'Rifler'),
        ('awper', 'AWPer'),
        ('entry_fragger', 'Entry Fragger'),
        ('support', 'Support'),
        ('igl', 'In-Game Leader'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='rifler')
    joined_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['team', 'player']
        ordering = ['joined_date']

    def __str__(self):
        return f"{self.player.username} - {self.team.name} ({self.role})"