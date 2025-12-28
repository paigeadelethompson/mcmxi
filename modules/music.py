"""
Sopel module for Music APIs.
Supports 8 public APIs with no authentication required.
"""

from sopel import plugin
import json
import sys
import os
# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get_module_logger, HTTPClient, IRCFormatter

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


@plugin.command('music')
@plugin.command('music')
@plugin.example(f'.music')
def music_list(bot, trigger):
    """List all available Music APIs."""
    bot.say(f'Available Music APIs (8):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .music_info <name> for details')


@plugin.command('music_info')
@plugin.example(f'.music_info <name>')
def music_info(bot, trigger):
    """Get information about a specific Music API."""
    if not trigger.group(2):
        bot.say(f'Usage: .music_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('music_search')
@plugin.example(f'.music_search <query>')
def music_search(bot, trigger):
    """Search Music APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .music_search <query>')
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
        url_station = station.get('url', '')
        
        response = f"{formatter.bold(name)}"
        if country:
            response += f" {formatter.italic(f'({country})')}"
        if tags:
            tags_list = tags.split(',')[:2]
            response += f" | Tags: {formatter.monospace(', '.join(tags_list))}"
        
        bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Music APIs loaded."""
    bot.memory['music_loaded'] = True
    bot.memory['music_count'] = 8
    logger.info('Music module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['music_loaded'] = False
    logger.info('Music module unloaded')
