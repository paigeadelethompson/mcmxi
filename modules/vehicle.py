"""
Sopel module for Vehicle APIs.
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
        'name': 'Brazilian Vehicles and Prices',
        'description': 'Vehicles information from Fundação Instituto de Pesquisas Econômicas - Fipe',
        'link': 'https://deividfortuna.github.io/fipe/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'NHTSA',
        'description': 'NHTSA Product Information Catalog and Vehicle Listing',
        'link': 'https://vpic.nhtsa.dot.gov/api/',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('vehicle')
@plugin.command('vehicle')
@plugin.example(f'.vehicle')
def vehicle_list(bot, trigger):
    """List all available Vehicle APIs."""
    bot.say(f'Available Vehicle APIs (2):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .vehicle_info <name> for details')


@plugin.command('vehicle_info')
@plugin.example(f'.vehicle_info <name>')
def vehicle_info(bot, trigger):
    """Get information about a specific Vehicle API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .vehicle_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('vehicle_search')
@plugin.example(f'.vehicle_search <query>')
def vehicle_search(bot, trigger):
    """Search Vehicle APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .vehicle_search <query>')
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


@plugin.command('vin_nhtsa')
@plugin.example('.vin_nhtsa 1HGBH41JXMN109186')
def vin_nhtsa(bot, trigger):
    """Decode VIN using NHTSA API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .vin_nhtsa <VIN>')
        bot.notice(trigger.nick, 'Example: .vin_nhtsa 1HGBH41JXMN109186')
        return
    
    vin = trigger.group(2).strip().upper()
    logger.info(f'VIN lookup: {vin}')
    
    encoded_vin = http.quote(vin)
    url = f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{encoded_vin}?format=json'
    
    logger.debug(f'Decoding VIN: {url}')
    data = http.get(url)
    
    if not data or 'Results' not in data:
        bot.notice(trigger.nick, f'Failed to decode VIN "{vin}" or API error.')
        return
    
    results = data.get('Results', [])
    if not results:
        bot.notice(trigger.nick, f'No data found for VIN "{vin}"')
        return
    
    # Extract key information
    info = {}
    for item in results:
        variable = item.get('Variable', '')
        value = item.get('Value', '')
        if value and value != 'Not Applicable':
            if 'Make' in variable:
                info['make'] = value
            elif 'Model' in variable:
                info['model'] = value
            elif 'Model Year' in variable:
                info['year'] = value
            elif 'Vehicle Type' in variable:
                info['type'] = value
            elif 'Body Class' in variable:
                info['body'] = value
    
    if not info:
        bot.notice(trigger.nick, f'No vehicle information found for VIN "{vin}"')
        return
    
    response = f"VIN {formatter.monospace(vin)}:"
    if info.get('year'):
        response += f" {formatter.bold(info['year'])}"
    if info.get('make'):
        response += f" {formatter.bold(info['make'])}"
    if info.get('model'):
        response += f" {formatter.bold(info['model'])}"
    if info.get('type'):
        response += f" | Type: {formatter.italic(info['type'])}"
    if info.get('body'):
        response += f" | Body: {formatter.monospace(info['body'])}"
    
    bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Vehicle APIs loaded."""
    bot.memory['vehicle_loaded'] = True
    bot.memory['vehicle_count'] = 2
    logger.info('Vehicle module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['vehicle_loaded'] = False
    logger.info('Vehicle module unloaded')
