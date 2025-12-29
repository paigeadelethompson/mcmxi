"""
Sopel module for Podcasts APIs.
Supports 1 public APIs with no authentication required.
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
        'name': 'iTunes',
        'description': 'Apple Podcasts Directory',
        'link': 'https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/index.html#//apple_ref/doc/uid/TP40017632-CH3-SW1',
        'https': True,
        'cors': 'unknown',
    },
]







def setup(bot):
    """Module setup - Podcasts APIs loaded."""
    register_apis('podcasts', APIS)
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
