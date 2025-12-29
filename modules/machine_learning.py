"""
Sopel module for Machine Learning APIs.
Supports 2 public APIs with no authentication required.
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

def setup(bot):
    """Module setup - Machine Learning APIs loaded."""
    register_apis('machine_learning', APIS)
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
