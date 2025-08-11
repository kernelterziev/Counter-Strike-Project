from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    RANK_CHOICES = [
        ('silver', 'Silver'),
        ('gold_nova', 'Gold Nova'),
        ('master_guardian', 'Master Guardian'),
        ('legendary_eagle', 'Legendary Eagle'),
        ('supreme', 'Supreme'),
        ('global_elite', 'Global Elite'),
    ]

    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='silver')
    hours_played = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    favorite_weapon = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    country = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.rank})"