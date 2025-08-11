from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class WeaponStats(models.Model):
    WEAPON_CHOICES = [
        ('ak47', 'AK-47'),
        ('m4a4', 'M4A4'),
        ('m4a1s', 'M4A1-S'),
        ('awp', 'AWP'),
        ('deagle', 'Desert Eagle'),
        ('glock', 'Glock-18'),
        ('usp', 'USP-S'),
    ]

    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weapon_stats')
    weapon = models.CharField(max_length=20, choices=WEAPON_CHOICES)
    total_kills = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_shots = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    headshot_kills = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ['player', 'weapon']
        ordering = ['-total_kills']

    def __str__(self):
        return f"{self.player.username} - {self.weapon}"

    @property
    def headshot_percentage(self):
        if self.total_kills == 0:
            return 0
        return round((self.headshot_kills / self.total_kills) * 100, 1)

    @property
    def accuracy_percentage(self):
        if self.total_shots == 0:
            return 0
        return round((self.total_kills / self.total_shots) * 100, 1)


class MapStats(models.Model):
    MAP_CHOICES = [
        ('dust2', 'Dust 2'),
        ('mirage', 'Mirage'),
        ('inferno', 'Inferno'),
        ('cache', 'Cache'),
        ('overpass', 'Overpass'),
        ('train', 'Train'),
        ('cobblestone', 'Cobblestone'),
    ]

    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='map_stats')
    map_name = models.CharField(max_length=20, choices=MAP_CHOICES)
    matches_played = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    matches_won = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_kills = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_deaths = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ['player', 'map_name']
        ordering = ['-matches_played']

    def __str__(self):
        return f"{self.player.username} on {self.map_name}"

    @property
    def win_rate(self):
        if self.matches_played == 0:
            return 0
        return round((self.matches_won / self.matches_played) * 100, 1)

    @property
    def kd_ratio(self):
        if self.total_deaths == 0:
            return self.total_kills
        return round(self.total_kills / self.total_deaths, 2)