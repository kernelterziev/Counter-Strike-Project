from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from teams.models import Team, TeamMembership
from django.utils import timezone
import datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Load professional CS teams and players - Top 15'

    def handle(self, *args, **options):
        self.stdout.write('Loading Top 15 professional teams...')

        # Professional teams data
        pro_teams_data = [
            {
                'name': 'Vitality',
                'tag': 'VIT',
                'country': 'France',
                'ranking': 1,
                'prize_money': 1205000,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/tKILQYEpjHB5b7_iPjMNYg.svg',
                'founded': '2013-11-01',
                'players': [
                    {'username': 'apEX', 'real_name': 'Dan Madesclaire', 'role': 'igl', 'rating': 6.0},
                    {'username': 'ropz', 'real_name': 'Robin Kool', 'role': 'rifler', 'rating': 6.5},
                    {'username': 'ZywOo', 'real_name': 'Mathieu Herbaut', 'role': 'awper', 'rating': 7.2},
                    {'username': 'flameZ', 'real_name': 'Shahar Shushan', 'role': 'rifler', 'rating': 6.3},
                    {'username': 'mezii', 'real_name': 'William Merriman', 'role': 'support', 'rating': 6.1},
                ]
            },
            {
                'name': 'MOUZ',
                'tag': 'MOUZ',
                'country': 'Germany',
                'ranking': 2,
                'prize_money': 885000,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/zFLwAELOD25BLFnzLMWQKr.svg',
                'founded': '2002-01-01',
                'players': [
                    {'username': 'Brollan', 'real_name': 'Ludvig Brolin', 'role': 'rifler', 'rating': 6.8},
                    {'username': 'Spinx', 'real_name': 'Lotan Giladi', 'role': 'entry_fragger', 'rating': 6.4},
                    {'username': 'torzsi', 'real_name': 'Ádám Torzsás', 'role': 'awper', 'rating': 7.0},
                    {'username': 'Jimpphat', 'real_name': 'Jimi Salo', 'role': 'rifler', 'rating': 6.9},
                    {'username': 'xertioN', 'real_name': 'Dorian Berman', 'role': 'igl', 'rating': 5.9},
                ]
            },
            {
                'name': 'Team Spirit',
                'tag': 'SPIRIT',
                'country': 'Russia',
                'ranking': 3,
                'prize_money': 750000,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/8-jcfYLnRDm2xPCHnBKZdw.svg',
                'founded': '2015-10-01',
                'players': [
                    {'username': 'chopper', 'real_name': 'Leonid Vishnyakov', 'role': 'igl', 'rating': 6.1},
                    {'username': 'sh1ro', 'real_name': 'Dmitry Sokolov', 'role': 'rifler', 'rating': 6.7},
                    {'username': 'zont1x', 'real_name': 'Nikolay Zontov', 'role': 'support', 'rating': 6.2},
                    {'username': 'donk', 'real_name': 'Danil Kryshkovets', 'role': 'rifler', 'rating': 7.5},
                    {'username': 'zweih', 'real_name': 'Dmitriy Kryshkovets', 'role': 'awper', 'rating': 6.0},
                ]
            },
            {
                'name': 'Falcons',
                'tag': 'FALCONS',
                'country': 'Saudi Arabia',
                'ranking': 4,
                'prize_money': 584500,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/QRDd5bqKFJHOpKG1VNxB7w.svg',
                'founded': '2017-05-01',
                'players': [
                    {'username': 'NiKo', 'real_name': 'Nikola Kovač', 'role': 'rifler', 'rating': 7.1},
                    {'username': 'TeSeS', 'real_name': 'Sergey Rostovtsev', 'role': 'igl', 'rating': 6.0},
                    {'username': 'm0NESY', 'real_name': 'Ilya Osipov', 'role': 'awper', 'rating': 6.9},
                    {'username': 'kyxsan', 'real_name': 'Dmitriy Aliev', 'role': 'rifler', 'rating': 6.2},
                    {'username': 'kyousuke', 'real_name': 'Alexandre Crestani', 'role': 'support', 'rating': 5.8},
                ]
            },
            {
                'name': 'The MongolZ',
                'tag': 'MONGZ',
                'country': 'Mongolia',
                'ranking': 5,
                'prize_money': 404375,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/stKQd5fGj8sF47GVkBaQYn.svg',
                'founded': '2018-03-01',
                'players': [
                    {'username': 'Senzu', 'real_name': 'Ankhbayar Batbayar', 'role': 'rifler', 'rating': 6.5},
                    {'username': 'Techno4K', 'real_name': 'Batsaikhan Batkhuu', 'role': 'awper', 'rating': 6.8},
                    {'username': 'bLitz', 'real_name': 'Garidmagnai Byambasuren', 'role': 'entry_fragger',
                     'rating': 6.3},
                    {'username': 'mzinho', 'real_name': 'Munkhbold Sodbayar', 'role': 'igl', 'rating': 6.0},
                    {'username': '910', 'real_name': 'Batbayar Batsaikhan', 'role': 'support', 'rating': 6.2},
                ]
            },
            {
                'name': 'Astralis',
                'tag': 'AST',
                'country': 'Denmark',
                'ranking': 6,
                'prize_money': 374375,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/9bgRXpAuXKN0q4wI_QAfEg.svg',
                'founded': '2016-01-01',
                'players': [
                    {'username': 'device', 'real_name': 'Nicolai Reedtz', 'role': 'awper', 'rating': 6.5},
                    {'username': 'stavn', 'real_name': 'Martin Lund', 'role': 'rifler', 'rating': 6.7},
                    {'username': 'HooXi', 'real_name': 'Rasmus Nielsen', 'role': 'igl', 'rating': 5.8},
                    {'username': 'jabbi', 'real_name': 'Jakob Nygaard', 'role': 'rifler', 'rating': 6.4},
                    {'username': 'Staehr', 'real_name': 'Victor Staehr', 'role': 'entry_fragger', 'rating': 6.2},
                ]
            },
            {
                'name': 'TYLOO',
                'tag': 'TYLOO',
                'country': 'China',
                'ranking': 7,
                'prize_money': 286000,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/c9HM3_NjnSkU1MtmJL4WFQ.svg',
                'founded': '2007-01-01',
                'players': [
                    {'username': 'AttackeR', 'real_name': 'Yuhan Liang', 'role': 'rifler', 'rating': 6.3},
                    {'username': 'JamYoung', 'real_name': 'Jianfeng Yang', 'role': 'awper', 'rating': 6.6},
                    {'username': 'Jee', 'real_name': 'Hanxin Pei', 'role': 'igl', 'rating': 5.9},
                    {'username': 'Mercury', 'real_name': 'Tianyang He', 'role': 'entry_fragger', 'rating': 6.1},
                    {'username': 'Moseyuh', 'real_name': 'Minjie Wang', 'role': 'support', 'rating': 6.0},
                ]
            },
            {
                'name': 'FaZe Clan',
                'tag': 'FAZE',
                'country': 'United States',
                'ranking': 8,
                'prize_money': 278500,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/SMM7iCukUCcCTLb9J93Vig.svg',
                'founded': '2010-05-01',
                'players': [
                    {'username': 'rain', 'real_name': 'Håvard Nygaard', 'role': 'rifler', 'rating': 6.4},
                    {'username': 'karrigan', 'real_name': 'Finn Andersen', 'role': 'igl', 'rating': 5.9},
                    {'username': 'EliGE', 'real_name': 'Jonathan Jablonowski', 'role': 'rifler', 'rating': 6.5},
                    {'username': 'broky', 'real_name': 'Helvijs Saukants', 'role': 'awper', 'rating': 6.8},
                    {'username': 'frozen', 'real_name': 'Fredrik Ljungberg', 'role': 'support', 'rating': 6.3},
                ]
            },
            {
                'name': 'HEROIC',
                'tag': 'HEROIC',
                'country': 'Denmark',
                'ranking': 9,
                'prize_money': 249000,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/RyC0sgN1GjN1w5XrGQG5jk.svg',
                'founded': '2016-08-01',
                'players': [
                    {'username': 'tN1R', 'real_name': 'Nico Tamjidi', 'role': 'rifler', 'rating': 6.4},
                    {'username': 'nilo', 'real_name': 'Nils Graeser', 'role': 'awper', 'rating': 6.6},
                    {'username': 'LNZ', 'real_name': 'Laurentiu Tarlea', 'role': 'igl', 'rating': 6.0},
                    {'username': 'yxngstxr', 'real_name': 'Jeppe Rene Dyhring', 'role': 'entry_fragger', 'rating': 6.3},
                    {'username': 'alkarenn', 'real_name': 'Aleksi Jalli', 'role': 'support', 'rating': 5.8},
                ]
            },
            {
                'name': 'Natus Vincere',
                'tag': 'NAVI',
                'country': 'Ukraine',
                'ranking': 10,
                'prize_money': 203750,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/kixzGCSgTydKDZhaNSXJNn.svg',
                'founded': '2009-12-17',
                'players': [
                    {'username': 'Aleksib', 'real_name': 'Aleksi Virolainen', 'role': 'igl', 'rating': 6.0},
                    {'username': 'b1t', 'real_name': 'Valeriy Vakhovskiy', 'role': 'rifler', 'rating': 6.6},
                    {'username': 'iM', 'real_name': 'Mihai-Cosmin Ivan', 'role': 'awper', 'rating': 6.4},
                    {'username': 'w0nderful', 'real_name': 'Ihor Zhdanov', 'role': 'rifler', 'rating': 6.8},
                    {'username': 'makazze', 'real_name': 'Maksym Bugera', 'role': 'support', 'rating': 5.7},
                ]
            },
            {
                'name': 'G2 Esports',
                'tag': 'G2',
                'country': 'Germany',
                'ranking': 11,
                'prize_money': 200875,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/zFLwAELOD25BLFnzLMWQKr.svg',
                'founded': '2013-11-13',
                'players': [
                    {'username': 'huNter-', 'real_name': 'Nemanja Kovač', 'role': 'rifler', 'rating': 6.8},
                    {'username': 'malbsMd', 'real_name': 'Mario Samayoa', 'role': 'rifler', 'rating': 6.1},
                    {'username': 'SunPayus', 'real_name': 'Enzo Beaumont', 'role': 'igl', 'rating': 5.9},
                    {'username': 'HeavyGod', 'real_name': 'Nikita Martynenko', 'role': 'awper', 'rating': 6.3},
                    {'username': 'matys', 'real_name': 'Mateusz Wilczewski', 'role': 'support', 'rating': 6.0},
                ]
            },
            {
                'name': 'paiN Gaming',
                'tag': 'PAIN',
                'country': 'Brazil',
                'ranking': 12,
                'prize_money': 199625,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/f6-i_bU67BbMZhDZeTl4xS.svg',
                'founded': '2010-04-01',
                'players': [
                    {'username': 'biguzera', 'real_name': 'Vinicius Figueredo', 'role': 'awper', 'rating': 6.5},
                    {'username': 'dav1deuS', 'real_name': 'David Silva', 'role': 'rifler', 'rating': 6.3},
                    {'username': 'dgt', 'real_name': 'Douglas Carias', 'role': 'igl', 'rating': 5.8},
                    {'username': 'nqz', 'real_name': 'Nicolas Tamburini', 'role': 'entry_fragger', 'rating': 6.2},
                    {'username': 'snow', 'real_name': 'Gabriel Peixoto', 'role': 'support', 'rating': 6.0},
                ]
            },
            {
                'name': 'Aurora',
                'tag': 'AURORA',
                'country': 'Russia',
                'ranking': 13,
                'prize_money': 175750,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/b61Qz1TvXJnXGRlSf6v4fG.svg',
                'founded': '2022-01-01',
                'players': [
                    {'username': 'XANTARES', 'real_name': 'Ismailcan Dörtkardeş', 'role': 'rifler', 'rating': 6.7},
                    {'username': 'MAJ3R', 'real_name': 'Aidyn Turlybekov', 'role': 'rifler', 'rating': 6.1},
                    {'username': 'woxic', 'real_name': 'Özgür Eker', 'role': 'awper', 'rating': 6.4},
                    {'username': 'Wicadia', 'real_name': 'Vladislav Sukharev', 'role': 'igl', 'rating': 5.9},
                    {'username': 'jottAAA', 'real_name': 'Joel Lukiainen', 'role': 'support', 'rating': 6.0},
                ]
            },
            {
                'name': 'FURIA',
                'tag': 'FURIA',
                'country': 'Brazil',
                'ranking': 14,
                'prize_money': 171125,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/4XzWZtDO1qRqzRlgEHyO7C.svg',
                'founded': '2017-08-01',
                'players': [
                    {'username': 'FalleN', 'real_name': 'Gabriel Toledo', 'role': 'awper', 'rating': 6.2},
                    {'username': 'YEKINDAR', 'real_name': 'Mareks Gaļinskis', 'role': 'entry_fragger', 'rating': 6.5},
                    {'username': 'yuurih', 'real_name': 'Yuri Santos', 'role': 'rifler', 'rating': 6.4},
                    {'username': 'KSCERATO', 'real_name': 'Kaike Cerato', 'role': 'rifler', 'rating': 6.6},
                    {'username': 'molodoy', 'real_name': 'Vladislav Nesterov', 'role': 'support', 'rating': 5.8},
                ]
            },
            {
                'name': 'NAVI Junior',
                'tag': 'NAVIJR',
                'country': 'Ukraine',
                'ranking': 15,
                'prize_money': 158500,
                'logo_url': 'https://img-cdn.hltv.org/teamlogo/8-jcfYLnRDm2xPCHnBKZdw.svg',
                'founded': '2020-01-01',
                'players': [
                    {'username': 'r3salt', 'real_name': 'Ivan Kovalenko', 'role': 'igl', 'rating': 6.0},
                    {'username': 'trend', 'real_name': 'Vladyslav Shvets', 'role': 'rifler', 'rating': 6.3},
                    {'username': 'jackz', 'real_name': 'Audric Jug', 'role': 'entry_fragger', 'rating': 6.1},
                    {'username': 'fear', 'real_name': 'Bogdan Laursas', 'role': 'awper', 'rating': 6.4},
                    {'username': 'krasnal', 'real_name': 'Maksym Pronin', 'role': 'support', 'rating': 5.9},
                ]
            },
        ]

        for team_data in pro_teams_data:
            # Create team with proper founded date
            founded_date = datetime.datetime.strptime(team_data['founded'], '%Y-%m-%d').date()

            team, created = Team.objects.get_or_create(
                name=team_data['name'],
                defaults={
                    'tag': team_data['tag'],
                    'country': team_data['country'],
                    'is_professional': True,
                    'prize_money': team_data['prize_money'],
                    'world_ranking': team_data['ranking'],
                    'logo_url': team_data['logo_url'],
                    'is_active': True,
                    'founded_date': founded_date,
                }
            )

            if created:
                self.stdout.write(f'Created team: {team.name} (#{team_data["ranking"]})')

            # Create players
            captain = None
            for i, player_data in enumerate(team_data['players']):
                user, user_created = User.objects.get_or_create(
                    username=player_data['username'],
                    defaults={
                        'real_name': player_data['real_name'],
                        'is_professional': True,
                        'hltv_rating': player_data['rating'],
                        'rank': 'global_elite',  # All pros are Global Elite
                        'country': team_data['country'],
                        'hours_played': 10000,  # Professional level hours
                        'prize_money': team_data['prize_money'] // 5,  # Split team prize money
                    }
                )

                if user_created:
                    self.stdout.write(f'  Created player: {user.username} ({player_data["real_name"]})')

                # Create membership
                membership, mem_created = TeamMembership.objects.get_or_create(
                    team=team,
                    player=user,
                    defaults={
                        'role': player_data['role'],
                        'is_active': True,
                        'joined_date': founded_date,
                    }
                )

                # Set IGL as captain
                if player_data['role'] == 'igl':
                    captain = user

            # Set team captain (prefer IGL, fallback to first player)
            if captain and not team.captain:
                team.captain = captain
                team.save()
                self.stdout.write(f'  Set captain: {captain.username}')
            elif not team.captain and team_data['players']:
                fallback_captain = User.objects.get(username=team_data['players'][0]['username'])
                team.captain = fallback_captain
                team.save()
                self.stdout.write(f'  Set fallback captain: {fallback_captain.username}')

        self.stdout.write(self.style.SUCCESS('Successfully loaded all Top 15 professional teams!'))
        self.stdout.write(f'Total teams created: {Team.objects.filter(is_professional=True).count()}')
        self.stdout.write(f'Total pro players created: {User.objects.filter(is_professional=True).count()}')