from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from teams.models import Team

User = get_user_model()


class Match(models.Model):
    MATCH_TYPE_CHOICES = [
        ('casual', 'Casual'),
        ('competitive', 'Competitive'),
        ('tournament', 'Tournament'),
    ]

    MAP_CHOICES = [
        ('dust2', 'Dust 2'),
        ('mirage', 'Mirage'),
        ('inferno', 'Inferno'),
        ('cache', 'Cache'),
        ('overpass', 'Overpass'),
        ('train', 'Train'),
        ('cobblestone', 'Cobblestone'),
    ]

    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2')
    map_name = models.CharField(max_length=20, choices=MAP_CHOICES)
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES, default='competitive')
    team1_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(30)])
    team2_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(30)])
    match_date = models.DateTimeField(default=timezone.now)
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    is_finished = models.BooleanField(default=False)

    class Meta:
        ordering = ['-match_date']
        verbose_name_plural = 'matches'

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} on {self.map_name}"

    @property
    def winner(self):
        if not self.is_finished:
            return None
        return self.team1 if self.team1_score > self.team2_score else self.team2


class PlayerMatchStats(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='player_stats')
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_stats')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    kills = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    deaths = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    assists = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    headshots = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    damage_dealt = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ['match', 'player']
        ordering = ['-kills']

    def __str__(self):
        return f"{self.player.username} - {self.match}"

    @property
    def kd_ratio(self):
        return round(self.kills / max(self.deaths, 1), 2)