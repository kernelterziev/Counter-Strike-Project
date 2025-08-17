from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
import random
import hashlib
from datetime import datetime, date

User = get_user_model()


class Team(models.Model):
    is_professional = models.BooleanField(default=False)
    prize_money = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    world_ranking = models.IntegerField(null=True, blank=True)
    logo_url = models.URLField(blank=True)  # For official team logos
    official_website = models.URLField(blank=True)
    name = models.CharField(max_length=100, unique=True)
    tag = models.CharField(max_length=10, unique=True)  # Team tag like [NAVI]
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)
    founded_date = models.DateField(default=timezone.now)
    description = models.TextField(max_length=1000, blank=True)
    country = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    captain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='captained_teams')

    def get_realistic_founded_date(self):
        team_seed = int(hashlib.md5(str(self.id).encode()).hexdigest()[:8], 16)
        random.seed(team_seed)

        # Random year between 2010-2020
        year = random.randint(2010, 2020)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Safe day range

        return date(year, month, day)

    def get_country_flag(self):
        """Return flag emoji for country"""
        flag_map = {
            # Balkans & Eastern Europe
            'macedonia': '🇲🇰',
            'north macedonia': '🇲🇰',
            'bulgaria': '🇧🇬',
            'serbia': '🇷🇸',
            'greece': '🇬🇷',
            'albania': '🇦🇱',
            'kosovo': '🇽🇰',
            'montenegro': '🇲🇪',
            'bosnia': '🇧🇦',
            'croatia': '🇭🇷',
            'slovenia': '🇸🇮',
            'romania': '🇷🇴',

            # Western Europe
            'france': '🇫🇷',
            'germany': '🇩🇪',
            'spain': '🇪🇸',
            'italy': '🇮🇹',
            'netherlands': '🇳🇱',
            'uk': '🇬🇧',
            'united kingdom': '🇬🇧',
            'england': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
            'belgium': '🇧🇪',
            'austria': '🇦🇹',
            'switzerland': '🇨🇭',
            'portugal': '🇵🇹',

            # Nordic Countries
            'denmark': '🇩🇰',
            'sweden': '🇸🇪',
            'norway': '🇳🇴',
            'finland': '🇫🇮',
            'iceland': '🇮🇸',

            # Eastern Europe & CIS
            'russia': '🇷🇺',
            'russian federation': '🇷🇺',
            'ukraine': '🇺🇦',
            'poland': '🇵🇱',
            'czech republic': '🇨🇿',
            'slovakia': '🇸🇰',
            'hungary': '🇭🇺',
            'belarus': '🇧🇾',
            'estonia': '🇪🇪',
            'latvia': '🇱🇻',
            'lithuania': '🇱🇹',
            'kazakhstan': '🇰🇿',

            # Americas
            'usa': '🇺🇸',
            'united states': '🇺🇸',
            'canada': '🇨🇦',
            'brazil': '🇧🇷',
            'argentina': '🇦🇷',
            'chile': '🇨🇱',
            'mexico': '🇲🇽',
            'colombia': '🇨🇴',
            'peru': '🇵🇪',

            # Asia
            'china': '🇨🇳',
            'japan': '🇯🇵',
            'south korea': '🇰🇷',
            'korea': '🇰🇷',
            'mongolia': '🇲🇳',
            'thailand': '🇹🇭',
            'singapore': '🇸🇬',
            'malaysia': '🇲🇾',
            'indonesia': '🇮🇩',
            'philippines': '🇵🇭',
            'india': '🇮🇳',
            'pakistan': '🇵🇰',
            'bangladesh': '🇧🇩',
            'vietnam': '🇻🇳',

            # Middle East & Africa
            'turkey': '🇹🇷',
            'saudi arabia': '🇸🇦',
            'israel': '🇮🇱',
            'iran': '🇮🇷',
            'uae': '🇦🇪',
            'egypt': '🇪🇬',
            'south africa': '🇿🇦',
            'morocco': '🇲🇦',

            # Oceania
            'australia': '🇦🇺',
            'new zealand': '🇳🇿',
        }

        if self.country:
            country_lower = self.country.lower().strip()
            return flag_map.get(country_lower, '🌍')  # Default globe emoji
        return ''

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

    def get_realistic_joined_date(self):
        # Use combination of player ID and team ID for consistent randomness
        seed = int(hashlib.md5(f"{self.player.id}_{self.team.id}".encode()).hexdigest()[:8], 16)
        random.seed(seed)

        # Random year between 2015-2025
        year = random.randint(2015, 2025)
        month = random.randint(1, 12)

        # If it's 2025, limit to months that have passed
        if year == 2025:
            month = random.randint(1, 8)  # Up to August 2025

        day = random.randint(1, 28)  # Safe day range

        return datetime(year, month, day)

    class Meta:
        unique_together = ['team', 'player']
        ordering = ['joined_date']

    def __str__(self):
        return f"{self.player.username} - {self.team.name} ({self.role})"