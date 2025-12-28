"""
Sopel module for Data Validation APIs.
Supports 3 public APIs with no authentication required.
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
        'name': 'API Adresse',
        'description': 'Official French address validation service',
        'link': 'https://adresse.data.gouv.fr/api-doc/adresse',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Postman Echo',
        'description': 'Test api server to receive and return value from HTTP method',
        'link': 'https://www.postman-echo.com',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'PurgoMalum',
        'description': 'Content validator against profanity & obscenity',
        'link': 'http://www.purgomalum.com',
        'https': False,
        'cors': 'unknown',
    },
]


@plugin.command('data_validation')
@plugin.command('datavalidation')
@plugin.example(f'.data_validation')
def data_validation_list(bot, trigger):
    """List all available Data Validation APIs."""
    bot.say(f'Available Data Validation APIs (3):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .data_validation_info <name> for details')


@plugin.command('data_validation_info')
@plugin.example(f'.data_validation_info <name>')
def data_validation_info(bot, trigger):
    """Get information about a specific Data Validation API."""
    if not trigger.group(2):
        bot.say(f'Usage: .data_validation_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('data_validation_search')
@plugin.example(f'.data_validation_search <query>')
def data_validation_search(bot, trigger):
    """Search Data Validation APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .data_validation_search <query>')
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
    """Module setup - Data Validation APIs loaded."""
    bot.memory['data_validation_loaded'] = True
    bot.memory['data_validation_count'] = 3


def shutdown(bot):
    """Module shutdown."""
    bot.memory['data_validation_loaded'] = False


@plugin.command('filter_purgomalum')
@plugin.example('.filter_purgomalum test text')
def filter_purgomalum(bot, trigger):
    """Check and filter text for profanity/obscenity using PurgoMalum API."""
    # PurgoMalum: http://www.purgomalum.com
    # Endpoint: GET http://www.purgomalum.com/service/json?text={text}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .filter_purgomalum <text>')
        bot.notice(trigger.nick, 'Example: .filter_purgomalum test text')
        return
    
    text = trigger.group(2).strip()
    
    if len(text) > 1000:
        bot.notice(trigger.nick, 'Text is too long (max 1000 characters).')
        return
    
    logger.info('PurgoMalum profanity check')
    
    encoded_text = http.quote(text)
    url = f'http://www.purgomalum.com/service/json?text={encoded_text}'
    
    logger.debug(f'Checking text: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to check text.')
        return
    
    original = data.get('original', text)
    result = data.get('result', text)
    
    # Determine if text was filtered
    was_filtered = original != result
    
    if was_filtered:
        bot.say(f"{formatter.bold('PurgoMalum')}: {formatter.bold('Profanity detected')}")
        bot.say(f"Filtered: {formatter.monospace(result)}")
    else:
        bot.say(f"{formatter.bold('PurgoMalum')}: {formatter.bold('No profanity')} ✓")
