"""
Sopel module for Music APIs.
Supports 8 public APIs with no authentication required.
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
        'name': 'Bandsintown',
        'description': 'Music Events',
        'link': 'https://app.swaggerhub.com/apis/Bandsintown/PublicAPI/3.0.0',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Gaana',
        'description': 'API to retrieve song information from Gaana',
        'link': 'https://github.com/cyberboysumanjay/GaanaAPI',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Genrenator',
        'description': 'Music genre generator',
        'link': 'https://binaryjazz.us/genrenator-api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'JioSaavn',
        'description': 'API to retrieve song information, album meta data and many more from JioSaavn',
        'link': 'https://github.com/cyberboysumanjay/JioSaavnAPI',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'LRCLIB',
        'description': 'Crowdsourced lyrics',
        'link': 'https://lrclib.net/docs',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'MusicBrainz',
        'description': 'Music',
        'link': 'https://musicbrainz.org/doc/Development/XML_Web_Service/Version_2',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Openwhyd',
        'description': 'Download curated playlists of streaming tracks (YouTube, SoundCloud, etc...)',
        'link': 'https://openwhyd.github.io/openwhyd/API',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Radio Browser',
        'description': 'List of internet radio stations',
        'link': 'https://api.radio-browser.info/',
        'https': True,
        'cors': 'yes',
    },
]




@plugin.command('radio_radiobrowser')
@plugin.example('.radio_radiobrowser jazz')
@plugin.example('.radio_radiobrowser country')
def radio_radiobrowser(bot, trigger):
    """Search for internet radio stations using Radio Browser API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .radio_radiobrowser <genre/name>')
        return

    query = trigger.group(2).strip()
    logger.info(f'Radio search: {query}')

    encoded_query = http.quote(query)
    url = f'https://de1.api.radio-browser.info/json/stations/search?name={encoded_query}&limit=3'

    logger.debug(f'Searching radio stations: {url}')
    data = http.get(url)

    if not data or not isinstance(data, list):
        bot.notice(trigger.nick, 'No radio stations found or API error. Please try again.')
        return

    results = data[:3]

    if not results:
        bot.notice(trigger.nick, f'No radio stations found for "{query}"')
        return

    bot.say(f'Found {len(results)} station(s) for "{query}":')
    for station in results:
        name = station.get('name', 'Unknown')
        country = station.get('country', '')
        tags = station.get('tags', '')
        station.get('url', '')

        response = f"{formatter.bold(name)}"
        if country:
            response += f" {formatter.italic(f'({country})')}"
        if tags:
            tags_list = tags.split(',')[:2]
            response += f" | Tags: {formatter.monospace(', '.join(tags_list))}"

        bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Music APIs loaded."""
    register_apis('music', APIS)
    bot.memory['music_loaded'] = True
    bot.memory['music_count'] = 8
    logger.info('Music module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['music_loaded'] = False
    logger.info('Music module unloaded')
