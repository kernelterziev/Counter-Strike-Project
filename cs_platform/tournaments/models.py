from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from teams.models import Team

User = get_user_model()


class Tournament(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    prize_pool = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_teams = models.IntegerField(default=16, validators=[MinValueValidator(2)])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_tournaments')
    banner = models.ImageField(upload_to='tournament_banners/', blank=True, null=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class TournamentParticipation(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tournament_participations')
    registration_date = models.DateTimeField(default=timezone.now)
    placement = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    prize_won = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ['tournament', 'team']
        ordering = ['placement']

    def __str__(self):
        return f"{self.team.name} in {self.tournament.name}"