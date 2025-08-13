import asyncio
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Sum
from asgiref.sync import sync_to_async
from teams.models import Team
from matches.models import Match, PlayerMatchStats
from stats.models import WeaponStats, MapStats
from django.db import models


User = get_user_model()


async def async_leaderboard_data(request):
    """Async view for leaderboard data - simulates heavy computation"""

    # Simulate async data processing
    await asyncio.sleep(0.1)  # Simulate database processing time

    # Get top players async
    top_players_data = await sync_to_async(list)(
        User.objects.annotate(
            total_kills=Sum('match_stats__kills'),
            total_matches=Count('match_stats'),
            avg_rating=Avg('hltv_rating')
        ).filter(total_kills__gt=0).order_by('-total_kills')[:10].values(
            'username', 'total_kills', 'total_matches', 'rank', 'country'
        )
    )

    # Get top teams async
    top_teams_data = await sync_to_async(list)(
        Team.objects.filter(is_active=True).annotate(
            member_count=Count('memberships')
        ).order_by('world_ranking', '-founded_date')[:10].values(
            'name', 'tag', 'country', 'world_ranking', 'prize_money', 'member_count'
        )
    )

    # Get match statistics async
    total_matches = await sync_to_async(Match.objects.count)()
    finished_matches = await sync_to_async(Match.objects.filter(is_finished=True).count)()

    # Simulate concurrent data processing
    stats_tasks = [
        sync_to_async(WeaponStats.objects.count)(),
        sync_to_async(MapStats.objects.count)(),
        sync_to_async(User.objects.filter(is_professional=True).count)(),
    ]

    weapon_stats_count, map_stats_count, pro_players_count = await asyncio.gather(*stats_tasks)

    return JsonResponse({
        'status': 'success',
        'data': {
            'top_players': top_players_data,
            'top_teams': top_teams_data,
            'platform_stats': {
                'total_matches': total_matches,
                'finished_matches': finished_matches,
                'weapon_stats_records': weapon_stats_count,
                'map_stats_records': map_stats_count,
                'professional_players': pro_players_count,
            }
        },
        'processed_async': True
    })


async def async_player_stats(request, player_id):
    """Async view for individual player statistics"""

    try:
        # Get player data async
        player = await sync_to_async(User.objects.get)(id=player_id)

        # Simulate heavy stats computation
        await asyncio.sleep(0.2)

        # Get player stats concurrently
        stats_tasks = [
            sync_to_async(list)(player.match_stats.all()[:10].values(
                'kills', 'deaths', 'assists', 'match__map_name', 'match__match_date'
            )),
            sync_to_async(list)(player.weapon_stats.all()[:5].values(
                'weapon', 'total_kills', 'headshot_kills', 'total_shots'
            )),
            sync_to_async(player.match_stats.aggregate)(
                total_kills=Sum('kills'),
                total_deaths=Sum('deaths'),
                total_matches=Count('id'),
                avg_kills=Avg('kills')
            ),
        ]

        recent_matches, weapon_stats, aggregate_stats = await asyncio.gather(*stats_tasks)

        # Calculate K/D ratio
        kd_ratio = 0
        if aggregate_stats['total_deaths'] and aggregate_stats['total_deaths'] > 0:
            kd_ratio = round(aggregate_stats['total_kills'] / aggregate_stats['total_deaths'], 2)

        return JsonResponse({
            'status': 'success',
            'player': {
                'username': player.username,
                'real_name': player.real_name,
                'rank': player.rank,
                'country': player.country,
                'is_professional': player.is_professional,
                'hltv_rating': float(player.hltv_rating) if player.hltv_rating else None,
            },
            'stats': {
                'total_kills': aggregate_stats['total_kills'] or 0,
                'total_deaths': aggregate_stats['total_deaths'] or 0,
                'total_matches': aggregate_stats['total_matches'] or 0,
                'avg_kills_per_match': round(aggregate_stats['avg_kills'] or 0, 1),
                'kd_ratio': kd_ratio,
            },
            'recent_matches': recent_matches,
            'weapon_stats': weapon_stats,
            'processed_async': True
        })

    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Player not found'
        }, status=404)


async def async_team_performance(request, team_id):
    """Async view for team performance analytics"""

    try:
        # Get team data async
        team = await sync_to_async(Team.objects.get)(id=team_id)

        # Simulate complex analytics processing
        await asyncio.sleep(0.15)

        # Get team performance data concurrently
        performance_tasks = [
            sync_to_async(Match.objects.filter(team1=team).count)(),
            sync_to_async(Match.objects.filter(team2=team).count)(),
            sync_to_async(
                Match.objects.filter(team1=team, is_finished=True, team1_score__gt=models.F('team2_score')).count)(),
            sync_to_async(
                Match.objects.filter(team2=team, is_finished=True, team2_score__gt=models.F('team1_score')).count)(),
            sync_to_async(list)(team.memberships.filter(is_active=True).select_related('player').values(
                'player__username', 'player__real_name', 'role', 'player__hltv_rating'
            )),
        ]

        team1_matches, team2_matches, team1_wins, team2_wins, members = await asyncio.gather(*performance_tasks)

        total_matches = team1_matches + team2_matches
        total_wins = team1_wins + team2_wins
        win_rate = round((total_wins / max(total_matches, 1)) * 100, 1)

        return JsonResponse({
            'status': 'success',
            'team': {
                'name': team.name,
                'tag': team.tag,
                'country': team.country,
                'is_professional': team.is_professional,
                'world_ranking': team.world_ranking,
                'prize_money': float(team.prize_money) if team.prize_money else 0,
            },
            'performance': {
                'total_matches': total_matches,
                'total_wins': total_wins,
                'win_rate': win_rate,
                'matches_as_team1': team1_matches,
                'matches_as_team2': team2_matches,
            },
            'members': members,
            'processed_async': True
        })

    except Team.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Team not found'
        }, status=404)


# Async template view
async def async_dashboard(request):
    """Async dashboard view with template rendering"""

    # Simulate async data loading
    await asyncio.sleep(0.1)

    # Get dashboard data async
    context_data = await sync_to_async(lambda: {
        'total_players': User.objects.count(),
        'total_teams': Team.objects.filter(is_active=True).count(),
        'total_matches': Match.objects.count(),
        'pro_players': User.objects.filter(is_professional=True).count(),
    })()

    return render(request, 'stats/async_dashboard.html', {
        'stats': context_data,
        'is_async': True,
    })