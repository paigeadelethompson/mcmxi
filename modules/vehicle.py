"""
Sopel module for Vehicle APIs.
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
    register_apis('vehicle', APIS)
    bot.memory['vehicle_loaded'] = True
    bot.memory['vehicle_count'] = 2
    logger.info('Vehicle module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['vehicle_loaded'] = False
    logger.info('Vehicle module unloaded')
