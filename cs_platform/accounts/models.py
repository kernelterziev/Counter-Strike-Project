from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    is_professional = models.BooleanField(default=False)
    real_name = models.CharField(max_length=100, blank=True)
    profile_image_url = models.URLField(blank=True)  # For pro player official images
    hltv_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    prize_money = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    RANK_CHOICES = [
        ('silver', 'Silver'),
        ('gold_nova', 'Gold Nova'),
        ('master_guardian', 'Master Guardian'),
        ('legendary_eagle', 'Legendary Eagle'),
        ('supreme', 'Supreme'),
        ('global_elite', 'Global Elite'),
    ]

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
            return flag_map.get(country_lower, '🌍')
        return ''

    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='silver')
    hours_played = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    favorite_weapon = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    country = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.rank})"