"""
Sopel module for Open Source Projects APIs.
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
        'name': 'Countly',
        'description': 'Countly web analytics',
        'link': 'https://api.count.ly/reference',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Datamuse',
        'description': 'Word-finding query engine',
        'link': 'https://www.datamuse.com/api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Drupal.org',
        'description': 'Drupal.org',
        'link': 'https://www.drupal.org/drupalorg/docs/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Evil Insult Generator',
        'description': 'Evil Insults',
        'link': 'https://evilinsult.com/api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'GitHub Contribution Chart Generator',
        'description': 'Create an image of your GitHub contributions',
        'link': 'https://github-contributions.vercel.app',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'GitHub ReadMe Stats',
        'description': 'Add dynamically generated statistics to your GitHub profile ReadMe',
        'link': 'https://github.com/anuraghazra/github-readme-stats',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Metabase',
        'description': 'An open source Business Intelligence server to share data and analytics inside your company',
        'link': 'https://www.metabase.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Shields',
        'description': 'Concise, consistent, and legible badges in SVG and raster format',
        'link': 'https://shields.io/',
        'https': True,
        'cors': 'unknown',
    },
]

def setup(bot):
    """Module setup - Open Source Projects APIs loaded."""
    register_apis('open_source_projects', APIS)
    bot.memory['open_source_projects_loaded'] = True
    bot.memory['open_source_projects_count'] = 8

def shutdown(bot):
    """Module shutdown."""
    bot.memory['open_source_projects_loaded'] = False

@plugin.command('word_datamuse')
@plugin.example('`word_datamuse words like programming')
@plugin.example('`word_datamuse rhymes with cat')
@plugin.example('`word_datamuse means like happy')
def word_datamuse(bot, trigger):
    """Search for words using Datamuse API (synonyms, rhymes, related words)."""
    # Datamuse: https://www.datamuse.com/api/
    # Endpoint: GET https://api.datamuse.com/words?{params}
    # Supports: ml= (means like), sl= (sounds like), sp= (spelled like), rel_rhy= (rhymes with)

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `word_datamuse <query>')
        bot.notice(trigger.nick, 'Examples: .word_datamuse words like programming')
        bot.notice(trigger.nick, '          .word_datamuse rhymes with cat')
        bot.notice(trigger.nick, '          .word_datamuse means like happy')
        return

    query = trigger.group(2).strip()

    logger.info(f'Datamuse word search: {query}')

    # Parse query type
    query_lower = query.lower()
    params = {}

    if query_lower.startswith(('words like ', 'like ')):
        word = query_lower.replace('words like ', '').replace('like ', '').strip()
        params['ml'] = word
    elif query_lower.startswith(('rhymes with ', 'rhyme ')):
        word = query_lower.replace('rhymes with ', '').replace('rhyme ', '').strip()
        params['rel_rhy'] = word
    elif query_lower.startswith(('means like ', 'similar to ')):
        word = query_lower.replace('means like ', '').replace('similar to ', '').strip()
        params['ml'] = word
    elif query_lower.startswith(('sounds like ', 'sound ')):
        word = query_lower.replace('sounds like ', '').replace('sound ', '').strip()
        params['sl'] = word
    else:
        # Default to "means like"
        params['ml'] = query

    # Build URL
    param_str = '&'.join([f'{k}={http.quote(v)}' for k, v in params.items()])
    url = f'https://api.datamuse.com/words?{param_str}&max=5'

    logger.debug(f'Searching words: {url}')
    data = http.get(url)

    if not data or not isinstance(data, list):
        bot.notice(trigger.nick, 'Failed to search words.')
        return

    if len(data) == 0:
        bot.say(f'{formatter.bold("Datamuse")}: No words found for "{query}"')
        return

    words = [word_obj.get('word', '') for word_obj in data[:5] if word_obj.get('word')]

    if words:
        bot.say(f'{formatter.bold("Datamuse")} words: {formatter.italic(", ".join(words))}')
