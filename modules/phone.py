"""
Sopel module for Phone APIs.
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
        'name': 'Phone Specification',
        'description': 'Rest Api for Phone specifications',
        'link': 'https://github.com/azharimm/phone-specs-api',
        'https': True,
        'cors': 'yes',
    },
]







@plugin.command('phone_spec')
@plugin.example('`phone_spec iphone 14')
@plugin.example('`phone_spec samsung galaxy')
def phone_spec(bot, trigger):
    """Get phone specifications using Phone Specification API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `phone_spec <phone_name>')
        bot.notice(trigger.nick, 'Example: `phone_spec iphone 14')
        return

    phone_name = trigger.group(2).strip()
    logger.info(f'Phone spec lookup: {phone_name}')

    encoded_phone = http.quote(phone_name)
    url = f'https://phone-specs-api.azharimm.dev/search?query={encoded_phone}'

    logger.debug(f'Searching phone specs: {url}')
    data = http.get(url)

    if not data or 'data' not in data or not data['data']:
        bot.notice(trigger.nick, f'Phone "{phone_name}" not found or API error.')
        return

    phones = data.get('data', [])[:3]

    bot.say(f'Found {len(phones)} phone(s) for "{phone_name}":')
    for phone in phones:
        name = phone.get('phone_name', 'Unknown')
        brand = phone.get('brand', 'Unknown')
        os = phone.get('os', 'Unknown')
        storage = phone.get('storage', 'Unknown')
        ram = phone.get('ram', 'Unknown')
        release_date = phone.get('release_date', 'Unknown')

        response = f"{formatter.bold(name)}"
        if brand:
            response += f" {formatter.italic(f'({brand})')}"
        if os:
            response += f" | OS: {formatter.monospace(os)}"
        if storage:
            response += f" | Storage: {formatter.monospace(storage)}"
        if ram:
            response += f" | RAM: {formatter.monospace(ram)}"
        if release_date and release_date != 'Unknown':
            response += f" | Released: {formatter.monospace(release_date)}"

        bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Phone APIs loaded."""
    register_apis('phone', APIS)
    bot.memory['phone_loaded'] = True
    bot.memory['phone_count'] = 1
    logger.info('Phone module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['phone_loaded'] = False
    logger.info('Phone module unloaded')
