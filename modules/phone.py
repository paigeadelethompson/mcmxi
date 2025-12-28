"""
Sopel module for Phone APIs.
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
        'name': 'Phone Specification',
        'description': 'Rest Api for Phone specifications',
        'link': 'https://github.com/azharimm/phone-specs-api',
        'https': True,
        'cors': 'yes',
    },
]


@plugin.command('phone')
@plugin.command('phone')
@plugin.example(f'.phone')
def phone_list(bot, trigger):
    """List all available Phone APIs."""
    bot.say(f'Available Phone APIs (1):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .phone_info <name> for details')


@plugin.command('phone_info')
@plugin.example(f'.phone_info <name>')
def phone_info(bot, trigger):
    """Get information about a specific Phone API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .phone_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('phone_search')
@plugin.example(f'.phone_search <query>')
def phone_search(bot, trigger):
    """Search Phone APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .phone_search <query>')
        return

    query = trigger.group(2).strip().lower()
    results = []
    for api in APIS:
        if (query in api['name'].lower() or query in api['description'].lower()):
            results.append(api)

    if not results:
        bot.notice(trigger.nick, f'No APIs found matching: {trigger.group(2)}')
        return

    bot.say(f'Found {len(results)} API(s):')
    for api in results[:5]:  # Show first 5 results
        bot.say(f"- {api['name']}: {api['description'][:60]}")
    if len(results) > 5:
        bot.say(f'... and {len(results) - 5} more results')


@plugin.command('phone_spec')
@plugin.example('.phone_spec iphone 14')
@plugin.example('.phone_spec samsung galaxy')
def phone_spec(bot, trigger):
    """Get phone specifications using Phone Specification API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .phone_spec <phone_name>')
        bot.notice(trigger.nick, 'Example: .phone_spec iphone 14')
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
    bot.memory['phone_loaded'] = True
    bot.memory['phone_count'] = 1
    logger.info('Phone module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['phone_loaded'] = False
    logger.info('Phone module unloaded')
