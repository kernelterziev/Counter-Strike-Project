from rest_framework import serializers
from django.contrib.auth import get_user_model
from teams.models import Team, TeamMembership
from matches.models import Match, PlayerMatchStats
from tournaments.models import Tournament, TournamentParticipation
from stats.models import WeaponStats, MapStats

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    country_flag = serializers.CharField(source='get_country_flag', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'real_name', 'rank', 'country', 'country_flag',
            'hours_played', 'favorite_weapon', 'is_professional',
            'hltv_rating', 'prize_money', 'date_joined'
        ]


class TeamSerializer(serializers.ModelSerializer):
    country_flag = serializers.CharField(source='get_country_flag', read_only=True)
    member_count = serializers.IntegerField(source='memberships.count', read_only=True)
    captain_name = serializers.CharField(source='captain.username', read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'tag', 'country', 'country_flag', 'description',
            'founded_date', 'is_professional', 'world_ranking', 'prize_money',
            'logo_url', 'member_count', 'captain_name', 'is_active'
        ]


class TeamMembershipSerializer(serializers.ModelSerializer):
    player = UserSerializer(read_only=True)

    class Meta:
        model = TeamMembership
        fields = ['player', 'role', 'joined_date', 'is_active']


class TeamDetailSerializer(serializers.ModelSerializer):
    country_flag = serializers.CharField(source='get_country_flag', read_only=True)
    members = TeamMembershipSerializer(source='memberships', many=True, read_only=True)
    captain = UserSerializer(read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'tag', 'country', 'country_flag', 'description',
            'founded_date', 'is_professional', 'world_ranking', 'prize_money',
            'logo_url', 'captain', 'members', 'is_active'
        ]


class MatchSerializer(serializers.ModelSerializer):
    team1 = TeamSerializer(read_only=True)
    team2 = TeamSerializer(read_only=True)
    winner_name = serializers.CharField(source='winner.name', read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'team1', 'team2', 'map_name', 'match_type',
            'team1_score', 'team2_score', 'match_date', 'duration_minutes',
            'is_finished', 'winner_name'
        ]


class PlayerMatchStatsSerializer(serializers.ModelSerializer):
    player = UserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    kd_ratio = serializers.FloatField(read_only=True)

    class Meta:
        model = PlayerMatchStats
        fields = [
            'player', 'team', 'kills', 'deaths', 'assists',
            'headshots', 'damage_dealt', 'kd_ratio'
        ]


class TournamentSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    participant_count = serializers.IntegerField(source='participants.count', read_only=True)

    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'description', 'prize_pool', 'max_teams',
            'start_date', 'end_date', 'registration_deadline', 'status',
            'organizer', 'participant_count'
        ]


class WeaponStatsSerializer(serializers.ModelSerializer):
    player = UserSerializer(read_only=True)
    headshot_percentage = serializers.FloatField(read_only=True)
    accuracy_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = WeaponStats
        fields = [
            'player', 'weapon', 'total_kills', 'total_shots',
            'headshot_kills', 'headshot_percentage', 'accuracy_percentage'
        ]