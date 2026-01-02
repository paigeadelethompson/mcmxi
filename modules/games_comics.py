"""
Sopel module for Games & Comics APIs.
Supports 60 public APIs with no authentication required.
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
        'name': 'AmiiboAPI',
        'description': 'Nintendo Amiibo Information',
        'link': 'https://amiiboapi.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Atlas Academy',
        'description': 'API for Fate/Grand Order game data',
        'link': 'https://api.atlasacademy.io/docs',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Autochess VNG',
        'description': 'Rest Api for Autochess VNG',
        'link': 'https://github.com/didadadida93/autochess-vng-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Barter.VG',
        'description': 'Provides information about Game, DLC, Bundles, Giveaways, Trading',
        'link': 'https://github.com/bartervg/barter.vg/wiki',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Blue Archive',
        'description': 'Provides Blue Archive characters information',
        'link': 'https://github.com/arufars/api-blue-archive',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Board Game Geek',
        'description': 'Board games, RPG and videogames',
        'link': 'https://boardgamegeek.com/wiki/page/BGG_XML_API2',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Call of Duty',
        'description': 'Unofficial wrapper for the Call of Duty API with multi-language support.',
        'link': 'https://codapi.dev/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'CheapShark',
        'description': 'Steam/PC Game Prices and Deals',
        'link': 'https://www.cheapshark.com/api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Chess.com',
        'description': 'Chess.com read-only REST API',
        'link': 'https://www.chess.com/news/view/published-data-api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Comic Vine',
        'description': 'Comics',
        'link': 'https://comicvine.gamespot.com/api/documentation',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Crafatar',
        'description': 'API for Minecraft skins and faces',
        'link': 'https://crafatar.com',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Cross Universe',
        'description': 'Cross Universe Card Data',
        'link': 'https://crossuniverse.psychpsyo.com/apiDocs.html',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'CSGO',
        'description': 'An unofficial JSON API for Counter-Strike: Global Offensive',
        'link': 'https://bymykel.github.io/CSGO-API/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Deck of Cards',
        'description': 'Deck of Cards',
        'link': 'https://deckofcardsapi.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Digimon Information',
        'description': 'Provides information about digimon creatures',
        'link': 'https://digimon-api.vercel.app/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Digimon TCG',
        'description': 'Search for Digimon cards in digimoncard.io',
        'link': 'https://documenter.getpostman.com/view/14059948/TzecB4fH',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Disney',
        'description': 'Information of Disney characters',
        'link': 'https://disneyapi.dev',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Dungeons and Dragons',
        'description': 'Reference for 5th edition spells, classes, monsters, and more',
        'link': 'https://www.dnd5eapi.co/docs/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Dungeons and Dragons (Alternate)',
        'description': 'Includes all monsters and spells from the SRD (System Reference Document) as well as a search API',
        'link': 'https://open5e.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Eight Ball',
        'description': 'Fortune-telling API with random, sentiment-biased, and multi-language responses',
        'link': 'https://eightballapi.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'FFXIV Collect',
        'description': 'Final Fantasy XIV data on collectables',
        'link': 'https://ffxivcollect.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Final Fantasy XIV',
        'description': 'Final Fantasy XIV Game data API',
        'link': 'https://xivapi.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'FreeToGame',
        'description': 'Free-To-Play Games Database',
        'link': 'https://www.freetogame.com/api-doc',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'FunTranslations',
        'description': 'Translate Text into funny languages',
        'link': 'https://api.funtranslations.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'GamerPower',
        'description': 'Game Giveaways Tracker',
        'link': 'https://www.gamerpower.com/api-read',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Geek-Jokes',
        'description': 'Fetch a random geeky/programming related joke for use in all sorts of applications',
        'link': 'https://github.com/sameerkumar18/geek-joke-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Genshin Impact',
        'description': 'Genshin Impact game data',
        'link': 'https://genshin.dev',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'GraphQL Pokemon',
        'description': 'GraphQL powered Pokemon API. Supports generations 1 through 8',
        'link': 'https://github.com/favware/graphql-pokemon',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'GW2Spidy',
        'description': 'GW2Spidy API, Items data on the Guild Wars 2 Trade Market',
        'link': 'https://github.com/rubensayshi/gw2spidy/wiki',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Hyrule Compendium',
        'description': 'Data on all interactive items from The Legend of Zelda: BOTW',
        'link': 'https://github.com/gadhagod/Hyrule-Compendium-API',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Italian Jokes',
        'description': 'JSON API for getting jokes about Italians',
        'link': 'https://italian-jokes.vercel.app/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'JokeAPI',
        'description': 'Programming, Miscellaneous and Dark Jokes',
        'link': 'https://sv443.net/jokeapi/v2/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Magic The Gathering',
        'description': 'Magic The Gathering Game Information',
        'link': 'http://magicthegathering.io/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Minecraft Server Status',
        'description': 'API to get Information about a Minecraft Server',
        'link': 'https://api.mcsrvstat.us',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'MMO Games',
        'description': 'MMO Games Database, News and Giveaways',
        'link': 'https://www.mmobomb.com/api',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Monster Hunter World',
        'description': 'Monster Hunter World data',
        'link': 'https://docs.mhw-db.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'moogleAPI',
        'description': 'Final Fantasy franchise data',
        'link': 'https://www.moogleapi.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Trivia',
        'description': 'Trivia Questions',
        'link': 'https://opentdb.com/api_config.php',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'PlayerDB',
        'description': 'Query Minecraft, Steam and XBox Accounts',
        'link': 'https://playerdb.co/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Pokéapi',
        'description': 'Pokémon Information',
        'link': 'https://pokeapi.co',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'PokéAPI (GraphQL)',
        'description': 'The Unofficial GraphQL for PokeAPI',
        'link': 'https://github.com/mazipan/graphql-pokeapi',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Pokémon TCG',
        'description': 'Pokémon TCG Information',
        'link': 'https://pokemontcg.io',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Psychonauts',
        'description': 'Psychonauts World Characters Information and PSI Powers',
        'link': 'https://psychonauts-api.netlify.app/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Puyo Nexus',
        'description': 'Puyo Puyo information from Puyo Nexus Wiki',
        'link': 'https://github.com/deltadex7/puyodb-api-deno',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Raider',
        'description': 'Provides detailed character and guild rankings for Raiding and Mythic+ content in World of Warcraft',
        'link': 'https://raider.io/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Rick and Morty',
        'description': 'All the Rick and Morty information, including images',
        'link': 'https://rickandmortyapi.com',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'RuneScape',
        'description': 'RuneScape and OSRS RPGs information',
        'link': 'https://runescape.wiki/w/Application_programming_interface',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Sakura CardCaptor',
        'description': 'Sakura CardCaptor Cards Information',
        'link': 'https://github.com/JessVel/sakura-card-captor-api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Scryfall',
        'description': 'Magic: The Gathering database',
        'link': 'https://scryfall.com/docs/api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Steam',
        'description': 'Internal Steam Web API documentation',
        'link': 'https://github.com/Revadike/InternalSteamWebAPI/wiki',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'TCGdex',
        'description': 'Multi languages Pokémon TCG Information',
        'link': 'https://www.tcgdex.net/docs',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'TETR.IO',
        'description': 'TETR.IO Tetra Channel API',
        'link': 'https://tetr.io/about/api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Universalis',
        'description': 'Final Fantasy XIV market board data',
        'link': 'https://universalis.app/docs/index.html',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Valorant (non-official)',
        'description': 'An extensive API containing data of most Valorant in-game items, assets and more',
        'link': 'https://valorant-api.com',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Warface (non-official)',
        'description': 'Official API proxy with better data structure and more features',
        'link': 'https://api.wfstats.cf',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'When is next MCU film',
        'description': 'Upcoming MCU film information',
        'link': 'https://github.com/DiljotSG/MCU-Countdown/blob/develop/docs/API.md',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Wynncraft',
        'description': 'Wynncraft Information',
        'link': 'https://docs.wynncraft.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'xkcd',
        'description': 'Retrieve xkcd comics as JSON',
        'link': 'https://xkcd.com/json.html',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Yu-Gi-Oh!',
        'description': 'Yu-Gi-Oh! TCG Information',
        'link': 'https://db.ygoprodeck.com/api-guide/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Zelda',
        'description': 'The Legend of Zelda franchise data',
        'link': 'https://docs.zelda.fanapis.com/docs',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('games_comics')
@plugin.command('gamescomics')
@plugin.example('`games_comics')
def games_comics_list(bot, trigger):
    """List all available Games & Comics APIs."""
    bot.say('Available Games & Comics APIs (60):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use {prefix}games_comics_info <name> for details')


@plugin.command('games_comics_info')
@plugin.example('`games_comics_info <name>')
def games_comics_info(bot, trigger):
    """Get information about a specific Games & Comics API."""
    if not trigger.group(2):
        bot.say('Usage: `games_comics_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('games_comics_search')
@plugin.example('`games_comics_search <query>')
def games_comics_search(bot, trigger):
    """Search Games & Comics APIs by name or description."""
    if not trigger.group(2):
        bot.say('Usage: `games_comics_search <query>')
        return

    query = trigger.group(2).strip().lower()
    results = []
    for api in APIS:
        if (query in api['name'].lower() or query in api['description'].lower()):
            results.append(api)

    if not results:
        bot.say(f'No APIs found matching: {trigger.group(2)}')
        return

    bot.say(f'Found {len(results)} API(s):')
    for api in results[:5]:  # Show first 5 results
        bot.say(f"- {api['name']}: {api['description'][:60]}")
    if len(results) > 5:
        bot.say(f'... and {len(results) - 5} more results')


@plugin.command('pokemon_pokeapi')
@plugin.example('`pokemon_pokeapi pikachu')
@plugin.example('`pokemon_pokeapi 25')
def pokemon_pokeapi(bot, trigger):
    """Get Pokémon information using PokéAPI."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pokemon_pokeapi <name> or .pokemon_pokeapi <id>')
        return

    query = trigger.group(2).strip().lower()
    logger.info(f'Pokemon lookup: {query}')

    # PokéAPI accepts both ID and name in the path
    encoded_query = http.quote(query.lower())
    url = f'https://pokeapi.co/api/v2/pokemon/{encoded_query}/'

    logger.debug(f'Fetching Pokemon: {url}')
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, f'Pokémon "{query}" not found.')
        return

    name = data.get('name', 'Unknown').title()
    pokemon_id = data.get('id', '')
    height = data.get('height', 0) / 10  # Convert to meters
    weight = data.get('weight', 0) / 10  # Convert to kg
    types = [t['type']['name'] for t in data.get('types', [])]

    response = f"{formatter.bold(name)} {formatter.monospace(f'#{pokemon_id}')}"
    response += f" | Height: {formatter.monospace(f'{height}m')} | Weight: {formatter.monospace(f'{weight}kg')}"
    response += f" | Types: {formatter.italic(', '.join(types))}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('pokemon_graphql')
@plugin.example('`pokemon_graphql pokemon name:pikachu')
@plugin.example('`pokemon_graphql pokemon id:25')
@plugin.example('`pokemon_graphql pokemons generation:1 limit:5')
@plugin.example('`pokemon_graphql type fire')
def pokemon_graphql(bot, trigger):
    """Query Pokemon data using GraphQL Pokemon API (favware)."""
    # GraphQL Pokemon: https://github.com/favware/graphql-pokemon
    # Endpoint: https://graphqlpokemon.favware.tech/

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pokemon_graphql <type> [options]')
        bot.notice(trigger.nick, 'Types: pokemon, pokemons, type, types')
        bot.notice(trigger.nick, 'Examples: .pokemon_graphql pokemon name:pikachu')
        bot.notice(trigger.nick, '          .pokemon_graphql pokemon id:25')
        bot.notice(trigger.nick, '          .pokemon_graphql pokemons generation:1 limit:5')
        bot.notice(trigger.nick, '          .pokemon_graphql type fire')
        return

    query_parts = trigger.group(2).strip().split()
    query_type = query_parts[0].lower()

    # Parse options
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

    logger.info(f'GraphQL Pokemon query: {query_type}, options: {options}')

    gql_client = GraphQLClient('https://graphqlpokemon.favware.tech/')

    if query_type == 'pokemon':
        # Query single Pokemon by name or ID
        pokemon_id = options.get('id', '')
        pokemon_name = options.get('name', '')

        if not pokemon_id and not pokemon_name:
            bot.notice(trigger.nick, 'Usage: `pokemon_graphql pokemon name:<name> or id:<id>')
            return

        identifier = pokemon_id if pokemon_id else pokemon_name.lower()
        query = """
        query GetPokemon($id: String!) {
            getPokemonByDexNumber(number: $id) {
                num
                species
                types
                baseStats {
                    hp
                    attack
                    defense
                    specialattack
                    specialdefense
                    speed
                }
                height
                weight
            }
        }
        """
        result = gql_client.execute(query, {'id': identifier})

        if result and 'getPokemonByDexNumber' in result:
            pokemon = result.get('getPokemonByDexNumber')
            if not pokemon:
                bot.notice(trigger.nick, f'Pokemon "{identifier}" not found.')
                return

            num = pokemon.get('num', '')
            species = pokemon.get('species', 'Unknown')
            types = pokemon.get('types', [])
            stats = pokemon.get('baseStats', {})
            height = pokemon.get('height', '')
            weight = pokemon.get('weight', '')

            response = f"{formatter.bold(species)} {formatter.monospace(f'#{num}')}"
            if types:
                response += f" | Types: {formatter.italic(', '.join(types))}"
            if height:
                response += f" | Height: {formatter.monospace(height)}"
            if weight:
                response += f" | Weight: {formatter.monospace(weight)}"
            if stats:
                hp = stats.get('hp', 0)
                attack = stats.get('attack', 0)
                response += f" | HP: {formatter.bold(str(hp))} ATK: {formatter.bold(str(attack))}"
            bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, f'Failed to fetch Pokemon "{identifier}".')

    elif query_type == 'pokemons':
        # List Pokemon with optional filters
        generation = options.get('generation', '')

        query = """
        query GetPokemons($take: Int) {
            getAllPokemon(take: $take) {
                num
                species
                types
            }
        }
        """
        result = gql_client.execute(query, {'take': limit})

        if result and 'getAllPokemon' in result:
            pokemons = result.get('getAllPokemon', [])

            # Filter by generation if specified
            if generation:
                try:
                    gen_num = int(generation)
                    if gen_num >= 1 and gen_num <= 8:
                        # Filter by generation (rough approximation by number range)
                        gen_ranges = {
                            1: (1, 151), 2: (152, 251), 3: (252, 386),
                            4: (387, 493), 5: (494, 649), 6: (650, 721),
                            7: (722, 809), 8: (810, 898)
                        }
                        if gen_num in gen_ranges:
                            start, end = gen_ranges[gen_num]
                            pokemons = [p for p in pokemons if start <= int(p.get('num', 999)) <= end]
                except ValueError:
                    pass

            if not pokemons:
                bot.notice(trigger.nick, 'No Pokemon found matching criteria.')
                return

            bot.say(f'Pokemon (showing {min(limit, len(pokemons))}):')
            for pokemon in pokemons[:limit]:
                num = pokemon.get('num', '')
                species = pokemon.get('species', 'Unknown')
                types = pokemon.get('types', [])

                response = f"{formatter.bold(species)} {formatter.monospace(f'#{num}')}"
                if types:
                    response += f" | {formatter.italic(', '.join(types))}"
                bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, 'Failed to fetch Pokemon list.')

    elif query_type in ['type', 'types']:
        # Get type information
        type_name = options.get('name', ' '.join(query_parts[1:])).lower() if len(query_parts) > 1 else ''
        if not type_name:
            bot.notice(trigger.nick, 'Usage: `pokemon_graphql type <type_name>')
            bot.notice(trigger.nick, 'Example: `pokemon_graphql type fire')
            return

        query = """
        query GetType($type: String!) {
            getType(type: $type) {
                name
                effectiveness {
                    doubleEffectiveTypes
                    doubleResistedTypes
                    effectiveTypes
                    effectlessTypes
                    normalTypes
                    resistedTypes
                }
            }
        }
        """
        result = gql_client.execute(query, {'type': type_name.capitalize()})

        if result and 'getType' in result:
            type_data = result.get('getType')
            if not type_data:
                bot.notice(trigger.nick, f'Type "{type_name}" not found.')
                return

            name = type_data.get('name', type_name)
            effectiveness = type_data.get('effectiveness', {})

            response = f"{formatter.bold(name)} Type"
            double_effective = effectiveness.get('doubleEffectiveTypes', [])
            if double_effective:
                response += f" | 2x effective vs: {formatter.italic(', '.join(double_effective))}"
            bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, f'Failed to fetch type "{type_name}".')

    else:
        bot.notice(trigger.nick, f'Unknown query type: {query_type}. Use: pokemon, pokemons, or type')


@plugin.command('pokeapi_graphql')
@plugin.example('`pokeapi_graphql pokemon name:pikachu')
@plugin.example('`pokeapi_graphql pokemon id:25')
@plugin.example('`pokeapi_graphql pokemons limit:10')
def pokeapi_graphql(bot, trigger):
    """Query Pokemon data using PokéAPI GraphQL (mazipan)."""
    # PokéAPI GraphQL: https://github.com/mazipan/graphql-pokeapi
    # Endpoint: https://beta.pokeapi.co/graphql/v1beta

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pokeapi_graphql <type> [options]')
        bot.notice(trigger.nick, 'Types: pokemon, pokemons')
        bot.notice(trigger.nick, 'Examples: .pokeapi_graphql pokemon name:pikachu')
        bot.notice(trigger.nick, '          .pokeapi_graphql pokemon id:25')
        bot.notice(trigger.nick, '          .pokeapi_graphql pokemons limit:10')
        return

    query_parts = trigger.group(2).strip().split()
    query_type = query_parts[0].lower()

    # Parse options
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

    logger.info(f'PokeAPI GraphQL query: {query_type}, options: {options}')

    # Try the GraphQL endpoint (may vary, this is a common pattern)
    gql_client = GraphQLClient('https://beta.pokeapi.co/graphql/v1beta')

    if query_type == 'pokemon':
        # Query single Pokemon by name or ID
        pokemon_id = options.get('id', '')
        pokemon_name = options.get('name', '').lower()

        if not pokemon_id and not pokemon_name:
            bot.notice(trigger.nick, 'Usage: `pokeapi_graphql pokemon name:<name> or id:<id>')
            return

        identifier = pokemon_id if pokemon_id else pokemon_name

        query = """
        query GetPokemon($id: Int, $name: String) {
            pokemon_v2_pokemon(where: {_or: [{id: {_eq: $id}}, {name: {_ilike: $name}}]}, limit: 1) {
                id
                name
                height
                weight
                pokemon_v2_pokemontypes {
                    pokemon_v2_type {
                        name
                    }
                }
                pokemon_v2_pokemonstats {
                    base_stat
                    pokemon_v2_stat {
                        name
                    }
                }
            }
        }
        """
        variables = {}
        if pokemon_id:
            variables['id'] = int(pokemon_id)
        else:
            variables['name'] = f'%{pokemon_name}%'

        result = gql_client.execute(query, variables)

        if result and 'pokemon_v2_pokemon' in result:
            pokemons = result.get('pokemon_v2_pokemon', [])
            if not pokemons:
                bot.notice(trigger.nick, f'Pokemon "{identifier}" not found.')
                return

            pokemon = pokemons[0]
            pokemon_id_actual = pokemon.get('id', '')
            name = pokemon.get('name', 'Unknown').title()
            height = pokemon.get('height', 0) / 10  # Convert to meters
            weight = pokemon.get('weight', 0) / 10  # Convert to kg
            types = []
            for type_data in pokemon.get('pokemon_v2_pokemontypes', []):
                type_name = type_data.get('pokemon_v2_type', {}).get('name', '')
                if type_name:
                    types.append(type_name)

            stats = {}
            for stat_data in pokemon.get('pokemon_v2_pokemonstats', []):
                stat_name = stat_data.get('pokemon_v2_stat', {}).get('name', '')
                base_stat = stat_data.get('base_stat', 0)
                if stat_name:
                    stats[stat_name] = base_stat

            response = f"{formatter.bold(name)} {formatter.monospace(f'#{pokemon_id_actual}')}"
            if types:
                response += f" | Types: {formatter.italic(', '.join(types))}"
            if height:
                response += f" | Height: {formatter.monospace(f'{height}m')}"
            if weight:
                response += f" | Weight: {formatter.monospace(f'{weight}kg')}"
            if 'hp' in stats:
                response += f" | HP: {formatter.bold(str(stats['hp']))}"
            bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, f'Failed to fetch Pokemon "{identifier}". The API endpoint may be different.')
            bot.notice(trigger.nick, 'Try using .pokemon_pokeapi for REST API instead.')

    elif query_type == 'pokemons':
        # List Pokemon
        query = """
        query GetPokemons($limit: Int!) {
            pokemon_v2_pokemon(limit: $limit, order_by: {id: asc}) {
                id
                name
                pokemon_v2_pokemontypes {
                    pokemon_v2_type {
                        name
                    }
                }
            }
        }
        """
        result = gql_client.execute(query, {'limit': limit})

        if result and 'pokemon_v2_pokemon' in result:
            pokemons = result.get('pokemon_v2_pokemon', [])
            if not pokemons:
                bot.notice(trigger.nick, 'No Pokemon found.')
                return

            bot.say(f'Pokemon (showing {len(pokemons)}):')
            for pokemon in pokemons:
                pokemon_id_actual = pokemon.get('id', '')
                name = pokemon.get('name', 'Unknown').title()
                types = []
                for type_data in pokemon.get('pokemon_v2_pokemontypes', []):
                    type_name = type_data.get('pokemon_v2_type', {}).get('name', '')
                    if type_name:
                        types.append(type_name)

                response = f"{formatter.bold(name)} {formatter.monospace(f'#{pokemon_id_actual}')}"
                if types:
                    response += f" | {formatter.italic(', '.join(types))}"
                bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, 'Failed to fetch Pokemon list. The API endpoint may be different.')
            bot.notice(trigger.nick, 'Try using .pokemon_pokeapi for REST API instead.')

    else:
        bot.notice(trigger.nick, f'Unknown query type: {query_type}. Use: pokemon or pokemons')


def setup(bot):
    """Module setup - Games & Comics APIs loaded."""
    register_apis('games_comics', APIS)
    bot.memory['games_comics_loaded'] = True
    bot.memory['games_comics_count'] = 60
    logger.info('Games & Comics module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['games_comics_loaded'] = False
    logger.info('Games & Comics module unloaded')
