"""
Sopel module for Sports & Fitness APIs.
Supports 14 public APIs with no authentication required.
"""

import os
import sys

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import GraphQLClient, get_command_prefix, HTTPClient, IRCFormatter, get_module_logger, register_apis

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)
formatter = IRCFormatter()


# API definitions
APIS = [
    {
        'name': 'balldontlie',
        'description': 'Balldontlie provides access to stats data from the NBA',
        'link': 'https://www.balldontlie.io',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'City Bikes',
        'description': 'City Bikes around the world',
        'link': 'https://api.citybik.es/v2/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'F1 API',
        'description': 'Open F1 API with realtime data',
        'link': 'https://f1api.dev',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Football (Soccer) Videos',
        'description': 'Embed codes for goals and highlights from Premier League, Bundesliga, Serie A and many more',
        'link': 'https://www.scorebat.com/video-api/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Football Standings',
        'description': 'Display football standings e.g epl, la liga, serie a etc. The data is based on espn site',
        'link': 'https://github.com/azharimm/football-standings-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'MLB Records and Stats',
        'description': 'Current and historical MLB statistics',
        'link': 'https://appac.github.io/mlb-data-api-docs/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'NBA GraphQL',
        'description': 'Advanced NBA Player, Team, and Season Statistics and Data',
        'link': 'https://nbaapi.com/graphql/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'NBA Stats',
        'description': 'NBA player statistics, season totals, advanced metrics, game data, and shot chart data',
        'link': 'https://api.server.nbaapi.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'NBA Stats',
        'description': 'Postman docs for comprehensive NBA player statistics, advanced metrics, and detailed shot chart data',
        'link': 'https://documenter.getpostman.com/view/25652688/2sB34Zs4xZ',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'NHL Records and Stats',
        'description': 'NHL historical data and statistics',
        'link': 'https://gitlab.com/dword4/nhlapi',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Oddsmagnet',
        'description': 'Odds history from multiple UK bookmakers',
        'link': 'https://oddsmagnet.com/oddsdata',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'OpenLigaDB',
        'description': 'Crowd sourced sports league results',
        'link': 'https://www.openligadb.de',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Squiggle',
        'description': 'Fixtures, results and predictions for Australian Football League matches',
        'link': 'https://api.squiggle.com.au',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'SuredBits',
        'description': 'Query sports data, including teams, players, games, scores and statistics',
        'link': 'https://suredbits.com/api/',
        'https': False,
        'cors': 'no',
    },
]


@plugin.command('sports_fitness')
@plugin.command('sportsfitness')
@plugin.example('`sports_fitness')
def sports_fitness_list(bot, trigger):
    """List all available Sports & Fitness APIs."""
    bot.say('Available Sports & Fitness APIs (14):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use {prefix}sports_fitness_info <name> for details')


@plugin.command('sports_fitness_info')
@plugin.example('`sports_fitness_info <name>')
def sports_fitness_info(bot, trigger):
    """Get information about a specific Sports & Fitness API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `sports_fitness_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('sports_fitness_search')
@plugin.example('`sports_fitness_search <query>')
def sports_fitness_search(bot, trigger):
    """Search Sports & Fitness APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `sports_fitness_search <query>')
        return

    query = trigger.group(2).strip().lower()
    results = []
    for api in APIS:
        if (query in api['name'].lower() or query in api['description'].lower()):
            results.append(api)

    if not results:
        bot.notice(trigger.nick, f'No APIs found matching: {trigger.group(2)}')
        return

    bot.say(f'Found {len(results)} API(s):')
    for api in results[:5]:  # Show first 5 results
        bot.say(f"- {api['name']}: {api['description'][:60]}")
    if len(results) > 5:
        bot.say(f'... and {len(results) - 5} more results')


@plugin.command('nba_balldontlie')
@plugin.example('`nba_balldontlie lebron james')
@plugin.example('`nba_balldontlie lakers')
def nba_balldontlie(bot, trigger):
    """Get NBA player or team stats using balldontlie API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `nba_balldontlie <player_name> or .nba_balldontlie <team_name>')
        return

    query = trigger.group(2).strip()
    logger.info(f'NBA lookup: {query}')

    encoded_query = http.quote(query)

    # Try player search first
    player_url = f'https://www.balldontlie.io/api/v1/players?search={encoded_query}&per_page=3'
    logger.debug(f'Searching NBA players: {player_url}')
    player_data = http.get(player_url)

    if player_data and 'data' in player_data and player_data['data']:
        players = player_data['data'][:3]
        bot.say(f'Found {len(players)} player(s) for "{query}":')
        for player in players:
            first_name = player.get('first_name', '')
            last_name = player.get('last_name', '')
            position = player.get('position', 'N/A')
            team = player.get('team', {})
            team_name = team.get('full_name', 'Free Agent') if team else 'Free Agent'

            response = f"{formatter.bold(f'{first_name} {last_name}')}"
            response += f" | Position: {formatter.monospace(position)} | Team: {formatter.italic(team_name)}"
            bot.say(formatter.truncate(response, max_len=400))
        return

    # Try team search
    team_url = f'https://www.balldontlie.io/api/v1/teams?search={encoded_query}'
    logger.debug(f'Searching NBA teams: {team_url}')
    team_data = http.get(team_url)

    if team_data and 'data' in team_data and team_data['data']:
        teams = team_data['data'][:3]
        bot.say(f'Found {len(teams)} team(s) for "{query}":')
        for team in teams:
            name = team.get('full_name', 'Unknown')
            city = team.get('city', '')
            conference = team.get('conference', '')
            division = team.get('division', '')

            response = f"{formatter.bold(name)}"
            if city:
                response += f" {formatter.italic(f'({city})')}"
            if conference:
                response += f" | {formatter.monospace(conference)} Conference"
            if division:
                response += f" - {formatter.monospace(division)} Division"

            bot.say(formatter.truncate(response, max_len=400))
        return

    bot.notice(trigger.nick, f'No NBA player or team found for "{query}"')


def setup(bot):
    """Module setup - Sports & Fitness APIs loaded."""
    register_apis('sports_fitness', APIS)
    bot.memory['sports_fitness_loaded'] = True
    bot.memory['sports_fitness_count'] = 14
    logger.info('Sports & Fitness module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['sports_fitness_loaded'] = False
    logger.info('Sports & Fitness module unloaded')


@plugin.command('bikes_citybikes')
@plugin.example('`bikes_citybikes paris')
@plugin.example('`bikes_citybikes velib')
def bikes_citybikes(bot, trigger):
    """Search for city bike networks using City Bikes API."""
    # City Bikes: https://api.citybik.es/v2/
    # Endpoint: GET https://api.citybik.es/v2/networks
    # Network: GET https://api.citybik.es/v2/networks/{network_id}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `bikes_citybikes <city_or_network_id>')
        bot.notice(trigger.nick, 'Examples: .bikes_citybikes paris')
        bot.notice(trigger.nick, '          .bikes_citybikes velib')
        return

    query = trigger.group(2).strip().lower()

    logger.info(f'City Bikes search: {query}')

    # First, search networks
    url = 'https://api.citybik.es/v2/networks'
    logger.debug(f'Fetching networks: {url}')
    data = http.get(url)

    if not data or 'networks' not in data:
        bot.notice(trigger.nick, 'Failed to fetch bike networks.')
        return

    networks = data.get('networks', [])

    # Filter networks by query
    matching = []
    for network in networks:
        network_id = network.get('id', '').lower()
        name = network.get('name', '').lower()
        city = network.get('location', {}).get('city', '').lower()

        if query in network_id or query in name or query in city:
            matching.append(network)

    if not matching:
        bot.notice(trigger.nick, f'No bike networks found for "{query}"')
        return

    # Show first match and get station info
    network = matching[0]
    network_id = network.get('id', '')
    network_name = network.get('name', 'Unknown')
    location = network.get('location', {})
    city = location.get('city', 'Unknown')
    country = location.get('country', '')

    response = f"{formatter.bold(network_name)}"
    response += f" ({formatter.italic(city)}"
    if country:
        response += f", {country}"
    response += ")"
    bot.say(response)

    # Get station info for this network
    station_url = f'https://api.citybik.es/v2/networks/{network_id}'
    logger.debug(f'Fetching stations: {station_url}')
    station_data = http.get(station_url)

    if station_data and 'network' in station_data:
        stations = station_data['network'].get('stations', [])
        if stations:
            # Show first few stations with bike availability
            available_stations = [s for s in stations[:5] if s.get('free_bikes', 0) > 0]
            if available_stations:
                bot.say(f"Stations with bikes (showing {min(3, len(available_stations))}):")
                for station in available_stations[:3]:
                    name = station.get('name', 'Unknown')
                    free_bikes = station.get('free_bikes', 0)
                    empty_slots = station.get('empty_slots', 0)
                    bot.say(f"  {formatter.bold(name)}: {formatter.monospace(f'{free_bikes} bikes')} available, {formatter.monospace(f'{empty_slots} slots')} free")


@plugin.command('f1_driver')
@plugin.example('`f1_driver 2023')
@plugin.example('`f1_driver 2024')
def f1_driver(bot, trigger):
    """Get F1 drivers for a year using F1 API."""
    # F1 API: https://f1api.dev
    # Endpoint: GET https://f1api.dev/api/drivers?year={year}

    year = trigger.group(2).strip() if trigger.group(2) else '2024'

    if not year.isdigit() or len(year) != 4:
        bot.notice(trigger.nick, 'Year must be 4 digits (e.g., 2024)')
        return

    logger.info(f'F1 drivers lookup: {year}')

    url = f'https://f1api.dev/api/drivers?year={year}'

    logger.debug(f'Fetching F1 drivers: {url}')
    data = http.get(url)

    if not data or 'drivers' not in data:
        bot.notice(trigger.nick, f'Failed to fetch F1 drivers for {year}.')
        return

    drivers = data.get('drivers', [])
    total = data.get('total', len(drivers))

    if not drivers:
        bot.notice(trigger.nick, f'No drivers found for year {year}.')
        return

    bot.say(f'F1 Drivers {year} (showing {min(5, len(drivers))} of {total}):')
    for driver in drivers[:5]:
        name = driver.get('name', '')
        surname = driver.get('surname', '')
        nationality = driver.get('nationality', 'Unknown')
        number = driver.get('number', '')

        response = f"{formatter.bold(f'{name} {surname}')}"
        if number:
            response += f" #{formatter.monospace(number)}"
        response += f" | {formatter.italic(nationality)}"
        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('nba_graphql')
@plugin.example('`nba_graphql teams')
@plugin.example('`nba_graphql players name:lebron')
@plugin.example('`nba_graphql players team:lakers limit:10')
@plugin.example('`nba_graphql player id:237')
@plugin.example('`nba_graphql team name:lakers')
def nba_graphql(bot, trigger):
    """Query NBA data using NBA GraphQL API. Supports teams, players, and more."""
    # NBA GraphQL: https://nbaapi.com/graphql/
    # Endpoint: POST https://nbaapi.com/graphql/

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `nba_graphql <type> [options]')
        bot.notice(trigger.nick, 'Types: teams, players, player, team')
        bot.notice(trigger.nick, 'Examples: .nba_graphql teams')
        bot.notice(trigger.nick, '          .nba_graphql players name:lebron')
        bot.notice(trigger.nick, '          .nba_graphql players team:lakers limit:10')
        bot.notice(trigger.nick, '          .nba_graphql player id:237')
        bot.notice(trigger.nick, '          .nba_graphql team name:lakers')
        return

    query_parts = trigger.group(2).strip().split()
    query_type = query_parts[0].lower()

    # Parse options (e.g., name:lebron, team:lakers, id:237, limit:5)
    options = {}
    limit = 5
    for part in query_parts[1:]:
        if ':' in part:
            key, value = part.split(':', 1)
            options[key.lower()] = value
            if key.lower() == 'limit':
                try:
                    limit = int(value)
                    if limit < 1 or limit > 20:
                        limit = 5
                except ValueError:
                    limit = 5

    logger.info(f'NBA GraphQL query: {query_type}, options: {options}')

    gql_client = GraphQLClient('https://nbaapi.com/graphql/')
    result = None

    # Build GraphQL query based on type
    if query_type == 'teams':
        # Query all teams
        query = """
        query GetTeams {
            teams {
                id
                name
                city
                conference
                division
            }
        }
        """
        result = gql_client.execute(query)

        if result and 'teams' in result:
            teams = result.get('teams', [])
            # Filter by name if provided
            if 'name' in options:
                search_name = options['name'].lower()
                teams = [t for t in teams if search_name in t.get('name', '').lower() or search_name in t.get('city', '').lower()]

            if not teams:
                bot.notice(trigger.nick, 'No teams found matching your criteria.')
                return

            bot.say(f'NBA Teams (showing {min(limit, len(teams))}):')
            for team in teams[:limit]:
                name = team.get('name', 'Unknown')
                city = team.get('city', '')
                conference = team.get('conference', '')
                division = team.get('division', '')

                response = f"{formatter.bold(name)}"
                if city:
                    response += f" ({formatter.italic(city)})"
                if conference:
                    response += f" | {formatter.monospace(conference)}"
                if division:
                    response += f" {formatter.monospace(division)}"
                bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, 'Failed to query teams. Try .nba_balldontlie for NBA data.')

    elif query_type == 'players':
        # Query players with optional filters
        query = """
        query GetPlayers($limit: Int) {
            players(limit: $limit) {
                id
                firstName
                lastName
                team {
                    id
                    name
                    city
                }
                position
            }
        }
        """
        result = gql_client.execute(query, {'limit': limit})

        if result and 'players' in result:
            players = result.get('players', [])

            # Filter by name if provided
            if 'name' in options:
                search_name = options['name'].lower()
                players = [p for p in players if search_name in p.get('firstName', '').lower() or search_name in p.get('lastName', '').lower()]

            # Filter by team if provided
            if 'team' in options:
                search_team = options['team'].lower()
                players = [p for p in players if p.get('team') and (search_team in p['team'].get('name', '').lower() or search_team in p['team'].get('city', '').lower())]

            if not players:
                bot.notice(trigger.nick, 'No players found matching your criteria.')
                return

            bot.say(f'NBA Players (showing {min(limit, len(players))}):')
            for player in players[:limit]:
                first = player.get('firstName', '')
                last = player.get('lastName', '')
                position = player.get('position', 'N/A')
                team = player.get('team', {})
                team_name = team.get('name', 'Free Agent') if team else 'Free Agent'

                response = f"{formatter.bold(f'{first} {last}')}"
                response += f" | {formatter.monospace(position)}"
                response += f" | Team: {formatter.italic(team_name)}"
                bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, 'Failed to query players. Try .nba_balldontlie for NBA data.')

    elif query_type == 'player':
        # Query single player by ID
        player_id = options.get('id', '')
        if not player_id:
            bot.notice(trigger.nick, 'Usage: `nba_graphql player id:<player_id>')
            return

        query = """
        query GetPlayer($id: ID!) {
            player(id: $id) {
                id
                firstName
                lastName
                team {
                    name
                    city
                }
                position
                height
                weight
            }
        }
        """
        result = gql_client.execute(query, {'id': player_id})

        if result and 'player' in result:
            player = result.get('player')
            if not player:
                bot.notice(trigger.nick, f'Player with ID {player_id} not found.')
                return

            first = player.get('firstName', '')
            last = player.get('lastName', '')
            position = player.get('position', 'N/A')
            team = player.get('team', {})
            team_name = team.get('name', 'Free Agent') if team else 'Free Agent'
            height = player.get('height', '')
            weight = player.get('weight', '')

            response = f"{formatter.bold(f'{first} {last}')}"
            response += f" | {formatter.monospace(position)}"
            response += f" | Team: {formatter.italic(team_name)}"
            if height:
                response += f" | Height: {formatter.monospace(height)}"
            if weight:
                response += f" | Weight: {formatter.monospace(weight)}"
            bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, f'Failed to query player {player_id}.')

    elif query_type == 'team':
        # Query single team by name or ID
        team_name_filter = options.get('name', '')
        team_id = options.get('id', '')

        if not team_name_filter and not team_id:
            bot.notice(trigger.nick, 'Usage: `nba_graphql team name:<team_name> or .nba_graphql team id:<team_id>')
            return

        # First get all teams to find the one we want
        query = """
        query GetTeams {
            teams {
                id
                name
                city
                conference
                division
            }
        }
        """
        result = gql_client.execute(query)

        if result and 'teams' in result:
            teams = result.get('teams', [])

            # Filter by name or ID
            if team_id:
                teams = [t for t in teams if str(t.get('id', '')) == team_id]
            elif team_name_filter:
                search_name = team_name_filter.lower()
                teams = [t for t in teams if search_name in t.get('name', '').lower() or search_name in t.get('city', '').lower()]

            if not teams:
                bot.notice(trigger.nick, 'Team not found.')
                return

            team = teams[0]
            name = team.get('name', 'Unknown')
            city = team.get('city', '')
            conference = team.get('conference', '')
            division = team.get('division', '')

            response = f"{formatter.bold(name)}"
            if city:
                response += f" ({formatter.italic(city)})"
            response += f" | {formatter.monospace(conference)} {formatter.monospace(division)}"
            bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, 'Failed to query team.')

    else:
        bot.notice(trigger.nick, f'Unknown query type: {query_type}. Use: teams, players, player, or team')
        if not result:
            bot.notice(trigger.nick, 'Note: NBA GraphQL API may require authentication or have a different schema.')
            bot.notice(trigger.nick, 'Try using .nba_balldontlie for NBA data instead.')


@plugin.command('football_openligadb')
@plugin.example('`football_openligadb bl1')
def football_openligadb(bot, trigger):
    """Get German Bundesliga match data using OpenLigaDB API."""
    # OpenLigaDB: https://www.openligadb.de
    # Endpoint: GET https://www.openligadb.de/api/getmatchdata/{league}/{season}/{group}
    # Leagues: bl1 (Bundesliga), bl2 (2. Bundesliga), bl3 (3. Liga)

    league = trigger.group(2).strip().lower() if trigger.group(2) else 'bl1'

    # Validate league
    valid_leagues = ['bl1', 'bl2', 'bl3']
    if league not in valid_leagues:
        bot.notice(trigger.nick, f'Invalid league. Valid: {", ".join(valid_leagues)}')
        return

    logger.info(f'OpenLigaDB lookup: {league}')

    # Get current season (2024), group 1
    url = f'https://www.openligadb.de/api/getmatchdata/{league}/2024/1'

    logger.debug(f'Fetching matches: {url}')
    data = http.get(url)

    if not data or not isinstance(data, list):
        bot.notice(trigger.nick, 'Failed to fetch match data.')
        return

    if not data:
        bot.notice(trigger.nick, f'No matches found for {league}.')
        return

    # Show upcoming/recent matches
    matches = data[:5]
    league_name = {'bl1': 'Bundesliga', 'bl2': '2. Bundesliga', 'bl3': '3. Liga'}.get(league, league)

    bot.say(f'{formatter.bold(league_name)} matches (showing {len(matches)}):')
    for match in matches:
        team1 = match.get('Team1', {}).get('TeamName', 'Unknown')
        team2 = match.get('Team2', {}).get('TeamName', 'Unknown')
        match_date = match.get('MatchDateTime', '')
        result = match.get('MatchResults', [])

        response = f"{formatter.bold(team1)} vs {formatter.bold(team2)}"
        if result:
            # Get final result
            final_result = [r for r in result if r.get('ResultName') == 'Endergebnis']
            if final_result:
                score1 = final_result[0].get('PointsTeam1', '')
                score2 = final_result[0].get('PointsTeam2', '')
                response += f" | {formatter.monospace(f'{score1}-{score2}')}"
        if match_date:
            date_short = match_date[:10] if len(match_date) >= 10 else match_date
            response += f" | {formatter.monospace(date_short)}"

        bot.say(formatter.truncate(response, max_len=400))
