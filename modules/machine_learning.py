"""
Sopel module for Machine Learning APIs.
Supports 2 public APIs with no authentication required.
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
        'name': 'EXUDE-API',
        'description': 'Used for the primary ways for filtering the stopping, stemming words from the text data',
        'link': 'http://uttesh.com/exude-api/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Face-api.js',
        'description': 'JavaScript API for face detection, recognition, and emotion analysis using TensorFlow.js',
        'link': 'https://github.com/justadudewhohacks/face-api.js',
        'https': False,
        'cors': 'unknown',
    },
]


@plugin.command('machine_learning')
@plugin.command('machinelearning')
@plugin.example(f'.machine_learning')
def machine_learning_list(bot, trigger):
    """List all available Machine Learning APIs."""
    bot.say(f'Available Machine Learning APIs (2):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .machine_learning_info <name> for details')


@plugin.command('machine_learning_info')
@plugin.example(f'.machine_learning_info <name>')
def machine_learning_info(bot, trigger):
    """Get information about a specific Machine Learning API."""
    if not trigger.group(2):
        bot.say(f'Usage: .machine_learning_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('machine_learning_search')
@plugin.example(f'.machine_learning_search <query>')
def machine_learning_search(bot, trigger):
    """Search Machine Learning APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .machine_learning_search <query>')
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
    """Module setup - Machine Learning APIs loaded."""
    bot.memory['machine_learning_loaded'] = True
    bot.memory['machine_learning_count'] = 2


def shutdown(bot):
    """Module shutdown."""
    bot.memory['machine_learning_loaded'] = False


@plugin.command('stem_exude')
@plugin.example('.stem_exude running jumping')
def stem_exude(bot, trigger):
    """Stem and filter words from text using EXUDE-API."""
    # EXUDE-API: http://uttesh.com/exude-api/
    # Endpoint: GET http://uttesh.com/exude-api/Stemming/{text}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .stem_exude <text>')
        bot.notice(trigger.nick, 'Example: .stem_exude running jumping')
        return
    
    text = trigger.group(2).strip()
    
    if len(text) > 500:
        bot.notice(trigger.nick, 'Text is too long (max 500 characters).')
        return
    
    logger.info('EXUDE-API stemming')
    
    encoded_text = http.quote(text)
    url = f'http://uttesh.com/exude-api/Stemming/{encoded_text}'
    
    logger.debug(f'Stemming text: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to stem text.')
        return
    
    # Response is typically a string or JSON with stemmed words
    if isinstance(data, str):
        stemmed = data.strip()
    elif isinstance(data, dict):
        stemmed = data.get('result', data.get('stemmed', str(data)))
    else:
        stemmed = str(data)
    
    if stemmed:
        bot.say(f"{formatter.bold('EXUDE Stemming')}: {formatter.monospace(stemmed[:300])}")
