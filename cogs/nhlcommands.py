import discord
from discord.ext import commands, menus
import aiohttp
import datetime
import unidecode

blacklisted_stat_types = ['timeOnIce', 'powerPlayTimeOnIce', 'evenTimeOnIce', 'shortHandedTimeOnIce',
                          'timeOnIcePerGame', 'evenTimeOnIcePerGame', 'shortHandedTimeOnIcePerGame',
                          'powerPlayTimeOnIcePerGame', 'powerPlaySaves', 'shortHandedSaves', 'evenSaves',
                          'shortHandedShots', 'evenShots', 'powerPlayShots', 'powerPlaySavePercentage',
                          'shortHandedSavePercentage', 'evenStrengthSavePercentage', 'penaltyMinutes']

blacklisted_draft_types = ['id', 'ageInDays', 'ageInDaysForYear', 'birthDate', 'birthPlace', 'csPlayerId', 'draftDate',
                           'draftMasterId', 'draftYear', 'draftedByTeamId', 'playerId', 'firstName', 'height',
                           'lastName', 'removedOutright', 'removedOutrightWhy', 'shootsCatches', 'supplementalDraft',
                           'weight', 'pickInRound']

blacklisted_team_stat_types = ['evGGARatio', 'powerPlayOpportunities', 'powerPlayGoals',
                               'powerPlayGoalsAgainst', 'powerPlayOpportunities', 'penaltyKillOpportunities',
                               'shotsPerGame', 'shotsAllowed', 'winScoreFirst', 'winOppScoreFirst',
                               'winLeadFirstPer', 'winLeadSecondPer', 'winOutshootOpp', 'winOutshotByOpp',
                               'faceOffsTaken', 'faceOffsWon', 'faceOffsLost', 'faceOffWinPercentage',
                               'savePctg', 'savePctRank', 'shootingPctg', 'shootingPctRank']


# Period class to represent a period in a hockey game
class Period:
    def __init__(self, period, home, away):
        self.period = period
        self.home = home
        self.away = away


def get_nhl_draft_url(year, draft_round, team_id):
    if team_id is None and draft_round == 0:
        return 0
    elif draft_round == 0:
        return f'https://records.nhl.com/site/api/draft?cayenneExp=draftedByTeamId={team_id}%20and%20draftYear={year}'
    elif team_id is None:
        return f'https://records.nhl.com/site/api/draft?cayenneExp=draftYear={year}%20and%20roundNumber={draft_round}'
    else:
        return f'https://records.nhl.com/site/api/draft?cayenneExp=draftedByTeamId={team_id}%20and%20draftYear={year}' \
               f'%20and%20roundNumber={draft_round} '


def getTeamID(team: str, year: int):
    if team is None:  # returns None if team is none
        return None

    if team == "New Jersey Devils" or team == "NJD" or team == "Colorado Rockies" or team == "CLR" \
            or team == "Kansas City Scouts" or team == "KCS":
        if year < 1976:
            return 48
        elif year < 1982:
            return 35
        else:
            return 1
    elif team == "New York Islanders" or team == "NYI":
        return 2
    elif team == "New York Rangers" or team == "NYR":
        return 3
    elif team == "Philadelphia Flyers" or team == "PHI":
        return 4
    elif team == "Pittsburgh Penguins" or team == "PIT":
        return 5
    elif team == "Boston Bruins" or team == "BOS":
        return 6
    elif team == "Buffalo Sabres" or team == "BUF":
        return 7
    elif team == "Montreal Canadiens" or team == "MTL":
        return 8
    elif team == "Ottawa Senators" or team == "OTT" or team == "St Louis Eagles" or team == "SLE":
        if year < 1934:
            return 36
        elif year < 1935:
            return 45
        else:
            return 9
    elif team == "Toronto Maple Leafs" or team == "TOR":
        return 10

    elif team == "Atlanta Thrashers" or team == "ATL" or team == "Winnipeg Jets" or team == "WIN":
        if year < 2011:
            return 11
        else:
            return 52

    elif team == "Carolina Hurricanes" or team == "CAR" or team == "Hartford Whalers" or team == "HFD":
        if year < 1997:
            return 34
        else:
            return 12
    elif team == "Florida Panthers" or team == "FLA":
        return 13
    elif team == "Tampa Bay Lightning" or team == "TBL":
        return 14
    elif team == "Washington Capitols" or team == "WSH":
        return 15
    elif team == "Chicago Blackhawks" or team == "CHI":
        return 16
    elif team == "Detroit Red Wings" or team == "DET" or team == "Detroit Cougars" or team == "DCG" \
            or team == "Detroit Falcons" or team == "DFL":
        if year < 1930:
            return 40
        elif year < 1932:
            return 50
        else:
            return 17
    elif team == "Nashville Predators" or team == "NSH":
        return 18
    elif team == "St Louis Blues" or team == "STL":
        return 19
    elif team == "Calgary Flames" or team == "CGY" or team == "Atlanta Flames" or team == "AFM":
        if year < 1980:
            return 47
        else:
            return 20
    elif team == "Colorado Avalanche" or team == "COL" or team == "Quebec Nordiques" or team == "QUE":
        if year < 1995:
            return 32
        else:
            return 21
    elif team == "Edmonton Oilers" or team == "EDM":
        return 22
    elif team == "Vancouver Canucks" or team == "VAN":
        return 23
    elif team == "Anaheim Ducks" or team == "ANA":
        return 24
    elif team == "Dallas Stars" or team == "DAL" or team == "Minnesota North Stars" or team == "MNS":
        if year < 1993:
            return 31
        else:
            return 25
    elif team == "Los Angeles Kings" or team == "LAK":
        return 26
    elif team == "Arizona Coyotes" or team == "ARI" or team == "PHX":
        if 2014 > year > 1995:
            return 27
        elif year < 1996:
            return 33
        else:
            return 53
    elif team == "San Jose Sharks" or team == "SJS":
        return 28
    elif team == "Columbus Blue Jackets" or team == "CBJ":
        return 29
    elif team == "Minnesota Wild" or team == "MIN":
        return 30
    elif team == "Hamilton Tigers" or team == "HAM" or team == "Quebec Bulldogs" or team == "QBD":
        if year < 1920:
            return 42
        return 37
    elif team == "Pittsburgh Pirates" or team == "PIR" or team == "Philadelphia Quakers" or team == "QUA":
        if year < 1930:
            return 39
        else:
            return 38
    elif team == "Montreal Wanderers" or team == "MWN":
        return 41
    elif team == "Montreal Maroons" or team == "MMN":
        return 43
    elif team == "New York Americans" or team == "NYA" or team == "Brooklyn Americans" or team == "BRK":
        if year < 1941:
            return 44
        else:
            return 51
    elif team == "Oakland Seals" or team == "OAK" or team == "Cleveland Barons" or team == "CLE":
        if year < 1970:
            return 46
        else:
            return 49
    elif team == "Vegas Golden Knights" or team == "VGK":
        return 54
    elif team == "Seattle Kraken" or team == "SEA":
        return 55


class EmbedPages(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entries):
        return entries


async def send_season_stats(ctx, name, player_id, extended, season_start_year, season_end_year):
    season_string = str(season_start_year) + str(season_end_year)

    player_url = f"https://statsapi.web.nhl.com/api/v1/people/{player_id}" \
                 f"/stats?stats=yearByYear"
    seasons = []

    embed_list = []

    async with aiohttp.ClientSession() as cs:  # pulls data from the website
        async with cs.get(player_url) as r:
            res = await r.json()
            for items in res['stats']:
                for season in items['splits']:
                    embed = discord.Embed(
                        title=f"{name} {season_start_year}-{season_end_year} season"
                    )
                    seasons.append(season['season'])
                    if season['season'] == season_string:
                        embed_string = "```\n"
                        found = True
                        embed_string += f"{season['team']['name']}\n{season['league']['name']}\n\n"
                        stats = season['stat']
                        max_key_length = 21
                        for key, value in stats.items():
                            if extended:
                                if len(key) > max_key_length:
                                    max_key_length = len(key)
                            else:
                                if key not in blacklisted_stat_types:
                                    if len(key) > max_key_length:
                                        max_key_length = len(key)

                        for key, value in stats.items():
                            if extended:
                                key += ":"
                                if isinstance(value, float):
                                    value = round(value, 2)
                                embed_string += f"{key:<{max_key_length + 2}}{value}\n"
                            else:
                                if key not in blacklisted_stat_types:
                                    key += ":"
                                    if isinstance(value, float):
                                        value = round(value, 2)
                                    embed_string += f"{key:<{max_key_length + 2}}{value}\n"

                        embed_string += "```"
                        embed.description = embed_string
                        embed_list.append(embed)

    if not found:
        first_season = seasons[0][:4] + "-" + seasons[0][4:]
        last_season = seasons[len(seasons) - 1][:4] + "-" + seasons[len(seasons) - 1][4:]
        await ctx.send(f'That season isn\'t in the API, try a season between {first_season} and '
                       f'{last_season}')
    else:
        if len(embed_list) > 1:
            pages = menus.MenuPages(source=EmbedPages(embed_list), clear_reactions_after=True)
            await pages.start(ctx)
            return
        else:
            await ctx.send(embed=embed_list[0])


async def send_seasons_stats(ctx, name, player_id, extended):
    player_url = f"https://statsapi.web.nhl.com/api/v1/people/{player_id}" \
                 f"/stats?stats=yearByYear"

    embed_list = []

    async with aiohttp.ClientSession() as cs:  # pulls data from the website
        async with cs.get(player_url) as r:
            res = await r.json()
            for items in res['stats']:
                for season in items['splits']:
                    embed = discord.Embed(
                        title=f"{name} {season['season'][:4]}-{season['season'][4:]} season"
                    )
                    embed_string = "```\n"
                    embed_string += f"{season['team']['name']}\n{season['league']['name']}\n\n"
                    stats = season['stat']
                    max_key_length = 21
                    for key, value in stats.items():
                        if extended:
                            if len(key) > max_key_length:
                                max_key_length = len(key)
                        else:
                            if key not in blacklisted_stat_types:
                                if len(key) > max_key_length:
                                    max_key_length = len(key)
                    for key, value in stats.items():
                        if extended:
                            key += ":"
                            if isinstance(value, float):
                                value = round(value, 2)
                            embed_string += f"{key:<{max_key_length + 2}}{value}\n"
                        else:
                            if key not in blacklisted_stat_types:
                                key += ":"
                                if isinstance(value, float):
                                    value = round(value, 2)
                                embed_string += f"{key:<{max_key_length + 2}}{value}\n"

                    embed_string += "```"
                    embed.description = embed_string
                    embed_list.append(embed)

    pages = menus.MenuPages(source=EmbedPages(embed_list), clear_reactions_after=True)
    await pages.start(ctx)
    return


async def get_player_id(ctx, name):
    name = unidecode.unidecode(name)  # decodes name for special symbols
    player_id = None

    name_list = name.split()
    name_list.insert(0, name)
    player_list = []
    for name in name_list:
        url = f"https://suggest.svc.nhl.com/svc/suggest/v1/minplayers/{name}"
        async with aiohttp.ClientSession() as cs:  # gets the data from the website
            async with cs.get(url) as r:
                res = await r.json()
                if not res['suggestions']:
                    pass
                elif len(res['suggestions']) == 1:
                    player = res['suggestions'][0]
                    values = player.split("|")
                    player_id = values[0]
                    break
                else:
                    lowercase_list = []
                    for name in name_list:
                        lowercase_list.append(name.lower())
                    for player in res['suggestions']:
                        values = player.split("|")
                        name_id_list = values[-1].split('-')
                        if len(lowercase_list) < 3:
                            player_list.append(values)
                            continue
                        if lowercase_list[1] == name_id_list[0] and lowercase_list[2] == name_id_list[1]:
                            player_id = values[0]
                            if values not in player_list:
                                player_list.append(values)

    if len(player_list) > 1:
        embed = discord.Embed(
            title="Sorry about this!",
            description="```\n"
                        "There are at least two people with that exact name, so here they are with their IDs, "
                        "if you see the person you are looking for use\n"
                        "\"howler nhl player id <command_name> <id> <name> <command arguments>\"```"
        )

        for player in player_list:
            embed.add_field(name=f"{player[2]} {player[1]} {player[10]}", value=f"ID: {player[0]}")

        await ctx.send(embed=embed)
        return 0
    elif player_id is None:
        await ctx.send("Player not found, try again.")
        return 0

    return player_id


async def send_career_stats(ctx, name, player_id, league, extended):
    if league == "NHL":
        league = "National Hockey League"

    player_url = f"https://statsapi.web.nhl.com/api/v1/people/{player_id}" \
                 f"/stats?stats=yearByYear"

    async with aiohttp.ClientSession() as cs:  # pulls data from the website
        async with cs.get(player_url) as r:
            res = await r.json()
            for items in res['stats']:
                career_stats_dict = {}
                for season in items['splits']:
                    if season['league']['name'] == league:
                        stats = season['stat']
                        for key, value in stats.items():
                            if key in career_stats_dict:
                                continue
                            else:
                                career_stats_dict[key] = 0

                        for key, value in stats.items():
                            if 'OnIce' in key:
                                minutes_played_add, seconds_add = value.split(':')
                                minutes_played = float(minutes_played_add) + round((float(seconds_add) / 60), 3)
                                career_stats_dict[key] += minutes_played
                            else:
                                career_stats_dict[key] += int(value)

    if league == "National Hockey League":
        league = "NHL"

    if 'faceOffPct' in career_stats_dict:
        career_stats_dict.pop('faceOffPct')

    if 'shotPct' in career_stats_dict:
        career_stats_dict['shotPct'] = career_stats_dict['goals'] / career_stats_dict['shots'] * 100

    if 'savePercentage' in career_stats_dict:
        if 'powerPlaySavePercentage' in career_stats_dict:
            career_stats_dict.pop('powerPlaySavePercentage')
            career_stats_dict.pop('shortHandedSavePercentage')
            career_stats_dict.pop('evenStrengthSavePercentage')
        career_stats_dict['savePercentage'] = career_stats_dict['saves'] / career_stats_dict['shotsAgainst']

    if 'goalAgainstAverage' in career_stats_dict:
        career_stats_dict['goalAgainstAverage'] = (career_stats_dict['goalsAgainst'] * 60) / career_stats_dict[
            'timeOnIce']

    embed = discord.Embed(
        title=f"{name} Career Stats {league}"
    )

    embed_string = "```\n"
    max_key_length = 21
    for key, value in career_stats_dict.items():
        if extended:
            if len(key) > max_key_length:
                max_key_length = len(key)
        else:
            if key not in blacklisted_stat_types:
                if len(key) > max_key_length:
                    max_key_length = len(key)
    for key, value in career_stats_dict.items():
        if extended:
            key += ":"
            if isinstance(value, float):
                value = round(value, 3)
            embed_string += f"{key:<{max_key_length + 2}}{value}\n"
        else:
            if key not in blacklisted_stat_types:
                key += ":"
                if isinstance(value, float):
                    value = round(value, 3)
                embed_string += f"{key:<{max_key_length + 2}}{value}\n"

    embed_string += "```"
    embed.description = embed_string

    await ctx.send(embed=embed)

    return


class NHLBot(commands.Cog, name="NHL"):
    def __init__(self, bot):
        self.bot = bot

    # COMMAND GROUPS ###################################################################################################

    @commands.group(brief="NHL Group Commands", invoke_without_command=True)
    async def nhl(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send("This is a group command, use `howler help nhl` to get list of subcommands under this command.")
            return

    @nhl.group(brief="Player Group Commands", invoke_without_command=True)
    async def player(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send("This is a group command, use `howler help nhl player` to get list of subcommands under this command.")
            return

    @player.group(brief="ID Group Commands", invoke_without_command=True)
    async def id(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send("This is a group command, use `howler help nhl player id` to get list of subcommands under this command.")
            return

    @nhl.group(brief="Team Group Commands", invoke_without_command=True)
    async def team(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send("This is a group command, use `howler help nhl team` to get list of subcommands under this command.")
            return

    # NHL COMMANDS #####################################################################################################

    @nhl.command(brief="Displays league standings", description="Displays league standings for current season if years are unspecified. Displays standings for specified season if years are specified.")
    async def standings(self, ctx, season_start_year=None, season_end_year=None):

        embed_list = []

        if season_start_year is None and season_end_year is None:
            url = "https://statsapi.web.nhl.com/api/v1/standings"
        elif season_start_year is None or season_end_year is None:
            await ctx.send("Missing a required argument")
            return
        else:
            url = f"https://statsapi.web.nhl.com/api/v1/standings?season={season_start_year}{season_end_year}"

        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()  # returns dict
                for record in res['records']:
                    embed = discord.Embed(
                        title=f"{record['division']['name']} division standings"
                    )
                    embed_string = "```\n"
                    for team in record['teamRecords']:
                        records = team['leagueRecord']
                        if 'ties' in records:
                            team_record = f"{records['wins']}-{records['losses']}-{records['ties']}-{records['ot']}"
                            embed_string += f"{team['team']['name']:<21} " \
                                            f"{team_record:<12}{team['points']}\n"
                        else:
                            team_record = f"{records['wins']}-{records['losses']}-{records['ot']}"
                            embed_string += f"{team['team']['name']:<21} " \
                                            f"{team_record:<10}{team['points']}\n"

                    embed_string += "```"
                    embed.description = embed_string
                    embed_list.append(embed)

        pages = menus.MenuPages(source=EmbedPages(embed_list), clear_reactions_after=True)
        await pages.start(ctx)

    # DRAFT COMMANDS ###################################################################################################

    @nhl.command(brief="Displays draft data for specified request.")
    async def draft(self, ctx, year: int, draft_round=0, team=None):

        embed_list = []

        team_id = getTeamID(team, year)

        url = get_nhl_draft_url(year, draft_round, team_id)
        if url == 0:
            await ctx.send("Invalid Arguments, input a team with round as 0 for all rounds, or input a round")
            return

        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()  # returns dict
                for player in res['data']:
                    embed_string = "```\n"
                    for key, value in player.items():
                        if key in blacklisted_draft_types:
                            continue
                        else:
                            embed = discord.Embed(
                                title=f"{year} draft"
                            )
                            key += ":"
                            embed_string += f"{key:<20}{value}\n"

                    embed_string += "```"
                    embed.description = embed_string
                    embed_list.append(embed)

        pages = menus.MenuPages(source=EmbedPages(embed_list), clear_reactions_after=True)
        await pages.start(ctx)

    # ID COMMANDS ######################################################################################################

    @id.command(name="season")
    async def _season(self, ctx, player_id, name, season_start_year, season_end_year, extended=None):
        await send_season_stats(ctx, name, player_id, extended, season_start_year, season_end_year)

    @id.command(name="seasons")
    async def _seasons(self, ctx, player_id, name, extended=None):
        await send_seasons_stats(ctx, name, player_id, extended)

    @id.command(name="career")
    async def _career(self, ctx, player_id, name, league, extended=None):
        await send_career_stats(ctx, name, player_id, league, extended)

    # PLAYER COMMANDS ##################################################################################################

    @player.command()
    async def season(self, ctx, name, season_start_year: int, season_end_year: int, extended=None):

        player_id = await get_player_id(ctx, name)
        if player_id == 0:
            return

        await send_season_stats(ctx, name, player_id, extended, season_start_year, season_end_year)

    @player.command()
    async def seasons(self, ctx, name, extended=None):
        player_id = await get_player_id(ctx, name)
        if player_id == 0:
            return

        await send_seasons_stats(ctx, name, player_id, extended)

    @player.command()
    async def career(self, ctx, name, league, extended=None):
        player_id = await get_player_id(ctx, name)
        if player_id == 0:
            return

        await send_career_stats(ctx, name, player_id, league, extended)

    # TEAM COMMANDS ####################################################################################################

    @team.command()
    async def stats(self, ctx, team, season_start_year, season_end_year, extended=None):
        season = str(season_start_year) + str(season_end_year)

        team_id = getTeamID(team, int(season_start_year))

        team_url = f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}?expand=team.stats&season={season}"
        embed_list = []

        async with aiohttp.ClientSession() as cs:
            async with cs.get(team_url) as r:
                res = await r.json()
                team = res['teams'][0]
                team_stats = team['teamStats'][0]
                for split in team_stats['splits']:
                    embed = discord.Embed(
                        title=f"{team['name']} Stats and Rankings {season_start_year}-{season_end_year}"
                    )
                    embed_string = "```\n"
                    max_key_length = 21
                    for key, value in split['stat'].items():
                        if extended:
                            if len(key) > max_key_length:
                                max_key_length = len(key)
                        else:
                            if key not in blacklisted_team_stat_types:
                                if len(key) > max_key_length:
                                    max_key_length = len(key)
                    for key, value in split['stat'].items():
                        if extended:
                            key += ":"
                            if isinstance(value, float):
                                value = round(value, 2)
                            embed_string += f"{key:<{max_key_length + 2}}{value}\n"
                        else:
                            if key not in blacklisted_team_stat_types:
                                key += ":"
                                if isinstance(value, float):
                                    value = round(value, 2)
                                embed_string += f"{key:<{max_key_length + 2}}{value}\n"

                    embed_string += "```"
                    embed.description = embed_string
                    embed_list.append(embed)

        pages = menus.MenuPages(source=EmbedPages(embed_list), clear_reactions_after=True)
        await pages.start(ctx)

    @team.command()
    async def next(self, ctx, team):
        team_id = getTeamID(team, datetime.datetime.now().year)
        team_url = f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}?expand=team.schedule.next"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(team_url) as r:
                res = await r.json()
                for matchup in res['teams']:
                    if 'nextGameSchedule' in matchup:
                        for schedule in matchup['nextGameSchedule']['dates']:
                            for game in schedule['games']:
                                game_date = datetime.datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%S%f%z')
                                game_status = game['status']
                                away_team = game['teams']['away']
                                home_team = game['teams']['home']
                    else:
                        await ctx.send(
                            "Look, there's two things that could've happened here. One, you asked for a team that "
                            "doesn't exist, in which case this is your fault. "
                            " Two, I screwed up and you're allowed to yell at me. I hope it's the first one.")
                        return

        embed = discord.Embed(
            title=f"{away_team['team']['name']} AT {home_team['team']['name']}",
            description=f"```Date: {game_date} \nStatus: {game_status['detailedState']}```"
        )

        ot = 0
        if 'ot' in away_team['leagueRecord']:
            ot = away_team['leagueRecord']['ot']

        embed.add_field(name=f"{away_team['team']['name']}",
                        value=f"```Record: {away_team['leagueRecord']['wins']}-{away_team['leagueRecord']['losses']}-"
                              f"{ot}```")

        if 'ot' in home_team['leagueRecord']:
            ot = home_team['leagueRecord']['ot']

        embed.add_field(name=f"{home_team['team']['name']}",
                        value=f"```Record: {home_team['leagueRecord']['wins']}-{home_team['leagueRecord']['losses']}-"
                              f"{ot}```")

        await ctx.send(embed=embed)

    @team.command()
    async def last(self, ctx, team):
        period_list = []

        team_id = getTeamID(team, datetime.datetime.now().year)
        team_url = f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}?expand=team.schedule.previous"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(team_url) as r:
                res = await r.json()
                for matchup in res['teams']:
                    if 'previousGameSchedule' in matchup:
                        for schedule in matchup['previousGameSchedule']['dates']:
                            for game in schedule['games']:
                                game_date = datetime.datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%S%f%z')
                                game_status = game['status']
                                game_id = game['gamePk']
                                away_team = game['teams']['away']
                                home_team = game['teams']['home']
                    else:
                        await ctx.send(
                            "Look, there's two things that could've happened here. "
                            "One, you asked for a team that doesn't exist, in which case this is your fault."
                            "Two, I screwed up and you're allowed to yell at me. I hope it's the first one.")
                        return

        game_url = f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/linescore"

        async with aiohttp.ClientSession() as cs:
            async with cs.get(game_url) as r:
                res = await r.json()
                for period in res['periods']:
                    x = Period(period['ordinalNum'], period['home'], period['away'])
                    period_list.append(x)

        embed = discord.Embed(
            title=f"{away_team['team']['name']} AT {home_team['team']['name']}",
            description=f"```Date: {game_date} \nStatus: {game_status['detailedState']} \nScore: {away_team['score']}-"
                        f"{home_team['score']}```"
        )

        away_periods = ""
        home_periods = ""

        for period in period_list:
            away_periods += f"{period.period} period:\n Shots: {period.away['shotsOnGoal']}\n" \
                            f" Goals: {period.away['goals']}\n"
            home_periods += f"{period.period} period:\n Shots: {period.home['shotsOnGoal']}\n" \
                            f" Goals: {period.home['goals']}\n"

        embed.add_field(name=f"{away_team['team']['name']}",
                        value=f"```Record: {away_team['leagueRecord']['wins']}-{away_team['leagueRecord']['losses']}-"
                              f"{away_team['leagueRecord']['ot']}\n{away_periods}```")
        embed.add_field(name=f"{home_team['team']['name']}",
                        value=f"```Record: {home_team['leagueRecord']['wins']}-{home_team['leagueRecord']['losses']}-"
                              f"{home_team['leagueRecord']['ot']}\n{home_periods}```")

        await ctx.send(embed=embed)

    @team.command()
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def roster(self, ctx, team, season_start_year, season_end_year):
        forward_list = ['```\n']
        defencemen_list = ['```\n']
        goalie_list = ['```\n']

        player_lists = [forward_list, defencemen_list, goalie_list]

        team_id = getTeamID(team, int(season_start_year))
        if team_id is None:
            await ctx.send("Couldn't find that team, try again.")
            return
        season = str(season_start_year) + str(season_end_year)

        team_url = f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}?expand=team.roster&season={season}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(team_url) as r:
                res = await r.json()
                if 'teams' in res:
                    for team_dict in res['teams']:
                        for player in team_dict['roster']['roster']:
                            if 'jerseyNumber' in player:
                                player_string = f"{player['jerseyNumber']:<3}{player['position']['code']} " \
                                                f"{player['person']['fullName']}\n"
                            else:
                                player_string = f"{0:<3}{player['position']['code']} {player['person']['fullName']}\n"
                            if player['position']['code'] == "D":
                                defencemen_list.append(player_string)
                            elif player['position']['code'] == "G":
                                goalie_list.append(player_string)
                            else:
                                forward_list.append(player_string)
                else:
                    await ctx.send(f'I couldn\'t find {team} for the {season_start_year}-{season_end_year} season! '
                                   f'Sorry, blame the NHL. '
                                   f'Or blame yourself if it didn\'t exist then. Your fault.')
                    return

        forward_list.append("```")
        defencemen_list.append("```")
        goalie_list.append("```")

        type_list = ['Forwards', 'Defencemen', 'Goalies']

        embed_list = []

        for player_list, position_type in zip(player_lists, type_list):
            string = ''.join(player_list)
            embed = discord.Embed(
                title=f"{team} {season_start_year}-{season_end_year} {position_type}",
                description=string
            )
            embed_list.append(embed)

        pages = menus.MenuPages(source=EmbedPages(embed_list), clear_reactions_after=True)
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(NHLBot(bot))
