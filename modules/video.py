"""
Sopel module for Video APIs.
Supports 26 public APIs with no authentication required.
"""

import os
import sys

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, IRCFormatter, get_module_logger, register_apis

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)
formatter = IRCFormatter()


# API definitions
APIS = [
    {
        'name': 'An API of Ice And Fire',
        'description': 'Game Of Thrones API',
        'link': 'https://anapioficeandfire.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': "Bob's Burgers API",
        'description': "The Bob's Burgers API contains data for hundreds of characters, episodes, running gags, and images from the show",
        'link': 'https://bobsburgersapi.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Breaking Bad Quotes',
        'description': 'Some Breaking Bad quotes',
        'link': 'https://github.com/shevabam/breaking-bad-quotes',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Buffy the Vampire Slayer and Angel',
        'description': 'Get episode, cast and crew data from Buffy the Vampire Slayer and Angel',
        'link': 'https://github.com/Thatskat/btvs-angel-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Catalogopolis',
        'description': 'Doctor Who API',
        'link': 'https://api.catalogopolis.xyz/docs/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Czech Television',
        'description': 'TV programme of Czech TV',
        'link': 'http://www.ceskatelevize.cz/xml/tv-program/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Eurovision Song Contest',
        'description': 'Unofficial Eurovision Song Contest API',
        'link': 'https://eurovisionapi.runasp.net/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Final Space',
        'description': 'Final Space API',
        'link': 'https://finalspaceapi.com/docs/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Game of Thrones Quotes',
        'description': 'Some Game of Thrones quotes',
        'link': 'https://gameofthronesquotes.xyz/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Harry Potter Characters',
        'description': 'Harry Potter Characters Data with with imagery',
        'link': 'https://hp-api.onrender.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'IMDbOT',
        'description': 'Unofficial IMDb Movie / Series Information',
        'link': 'https://github.com/SpEcHiDe/IMDbOT',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Lucifer Quotes',
        'description': 'Returns Lucifer quotes',
        'link': 'https://github.com/shadowoff09/lucifer-quotes',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'MCU Countdown',
        'description': 'A Countdown to the next MCU Film',
        'link': 'https://github.com/DiljotSG/MCU-Countdown',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Movie Quote',
        'description': 'Random Movie and Series Quotes',
        'link': 'https://github.com/F4R4N/movie-quote/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Ron Swanson Quotes',
        'description': 'Television',
        'link': 'https://github.com/jamesseanwright/ron-swanson-quotes#ron-swanson-quotes-api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'South Park Quotes',
        'description': 'Get some quotes from South Park, mmkay!',
        'link': 'https://github.com/Thatskat/southpark-quotes-api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'STAPI',
        'description': 'Information on all things Star Trek',
        'link': 'https://stapi.co',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Star Wars Databank',
        'description': 'Info and data from the Star Wars databank in the form of an API',
        'link': 'https://starwars-databank.vercel.app/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Stranger Things Quotes',
        'description': 'Returns Stranger Things quotes',
        'link': 'https://github.com/shadowoff09/strangerthings-quotes',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Stromberg Quotes',
        'description': 'Returns Stromberg quotes and more',
        'link': 'https://www.stromberg-api.de/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Supernatural Quotes',
        'description': '100+ Supernatural quotes',
        'link': 'https://lidiakovac.github.io/supernatural-api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'SWAPI',
        'description': "All the Star Wars data you've ever wanted",
        'link': 'https://swapi.dev/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'SWAPI',
        'description': 'All things Star Wars',
        'link': 'https://www.swapi.tech',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'SWAPI GraphQL',
        'description': 'Star Wars GraphQL API',
        'link': 'https://graphql.org/swapi-graphql',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'ThronesApi',
        'description': 'Game Of Thrones Characters Data with imagery',
        'link': 'https://thronesapi.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'TVMaze',
        'description': 'TV Show Data',
        'link': 'http://www.tvmaze.com/api',
        'https': False,
        'cors': 'unknown',
    },
]







def setup(bot):
    """Module setup - Video APIs loaded."""
    register_apis('video', APIS)
    bot.memory['video_loaded'] = True
    bot.memory['video_count'] = 26


def shutdown(bot):
    """Module shutdown."""
    bot.memory['video_loaded'] = False


@plugin.command('quote_breakingbad')
@plugin.example('`quote_breakingbad')
def quote_breakingbad(bot, trigger):
    """Get a random Breaking Bad quote."""
    # Breaking Bad Quotes: https://github.com/shevabam/breaking-bad-quotes
    # Endpoint: GET https://api.breakingbadquotes.xyz/v1/quotes
    # Returns: Array with quote object containing quote and author

    logger.info('Breaking Bad quote lookup')

    url = 'https://api.breakingbadquotes.xyz/v1/quotes'

    logger.debug(f'Fetching quote: {url}')
    data = http.get(url)

    if not data or not isinstance(data, list) or len(data) == 0:
        bot.notice(trigger.nick, 'Failed to fetch Breaking Bad quote.')
        return

    quote_obj = data[0]
    quote_text = quote_obj.get('quote', '')
    author = quote_obj.get('author', 'Unknown')

    response = f"{formatter.italic(quote_text)}"
    bot.say(formatter.truncate(response, max_len=400))
    if author:
        bot.say(f"  — {formatter.bold(author)}")
