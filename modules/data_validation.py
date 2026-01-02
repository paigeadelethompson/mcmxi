"""
Sopel module for Data Validation APIs.
Supports 3 public APIs with no authentication required.
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


def setup(bot):
    """Module setup - Data Validation APIs loaded."""
    register_apis('data_validation', APIS)
    bot.memory['data_validation_loaded'] = True
    bot.memory['data_validation_count'] = 3

def shutdown(bot):
    """Module shutdown."""
    bot.memory['data_validation_loaded'] = False

@plugin.command('filter_purgomalum')
@plugin.example('`filter_purgomalum test text')
def filter_purgomalum(bot, trigger):
    """Check and filter text for profanity/obscenity using PurgoMalum API."""
    # PurgoMalum: http://www.purgomalum.com
    # Endpoint: GET http://www.purgomalum.com/service/json?text={text}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `filter_purgomalum <text>')
        bot.notice(trigger.nick, 'Example: `filter_purgomalum test text')
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
