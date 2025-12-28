"""
Sopel module for Podcasts APIs.
Supports 1 public APIs with no authentication required.
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
        'name': 'iTunes',
        'description': 'Apple Podcasts Directory',
        'link': 'https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/index.html#//apple_ref/doc/uid/TP40017632-CH3-SW1',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('podcasts')
@plugin.command('podcasts')
@plugin.example(f'.podcasts')
def podcasts_list(bot, trigger):
    """List all available Podcasts APIs."""
    bot.say(f'Available Podcasts APIs (1):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .podcasts_info <name> for details')


@plugin.command('podcasts_info')
@plugin.example(f'.podcasts_info <name>')
def podcasts_info(bot, trigger):
    """Get information about a specific Podcasts API."""
    if not trigger.group(2):
        bot.say(f'Usage: .podcasts_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('podcasts_search')
@plugin.example(f'.podcasts_search <query>')
def podcasts_search(bot, trigger):
    """Search Podcasts APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .podcasts_search <query>')
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


def setup(bot):
    """Module setup - Podcasts APIs loaded."""
    bot.memory['podcasts_loaded'] = True
    bot.memory['podcasts_count'] = 1


def shutdown(bot):
    """Module shutdown."""
    bot.memory['podcasts_loaded'] = False


@plugin.command('podcast_itunes')
@plugin.example('.podcast_itunes python')
def podcast_itunes(bot, trigger):
    """Search for podcasts using iTunes/Apple Podcasts API."""
    # iTunes: https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/
    # Endpoint: GET https://itunes.apple.com/search?term={term}&media=podcast&limit=3
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .podcast_itunes <search_term>')
        bot.notice(trigger.nick, 'Example: .podcast_itunes python')
        return
    
    search_term = trigger.group(2).strip()
    
    logger.info(f'iTunes podcast search: {search_term}')
    
    encoded_term = http.quote(search_term)
    url = f'https://itunes.apple.com/search?term={encoded_term}&media=podcast&limit=3'
    
    logger.debug(f'Searching podcasts: {url}')
    data = http.get(url)
    
    if not data or 'results' not in data:
        bot.notice(trigger.nick, f'No podcasts found for "{search_term}" or API error.')
        return
    
    results = data.get('results', [])
    
    if len(results) == 0:
        bot.notice(trigger.nick, f'No podcasts found for "{search_term}"')
        return
    
    bot.say(f'Found {len(results)} podcast(s) for "{search_term}":')
    for podcast in results:
        name = podcast.get('collectionName', 'Unknown')
        artist = podcast.get('artistName', 'Unknown')
        genre = podcast.get('primaryGenreName', '')
        
        response = f"{formatter.bold(name)}"
        if artist:
            response += f" by {formatter.italic(artist)}"
        if genre:
            response += f" | {formatter.monospace(genre)}"
        bot.say(formatter.truncate(response, max_len=400))
