"""
Sopel module for HamDB.org amateur radio callsign lookups.
Uses HamDB REST API - no authentication required.
"""
import os
import sys
from typing import Dict, Optional

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, IRCFormatter, get_module_logger

logger = get_module_logger(__name__)
http = HTTPClient(max_size=1 * 1024 * 1024)  # 1MB max
formatter = IRCFormatter()

# HamDB API endpoint
HAMDB_API_URL = 'http://api.hamdb.org'
APP_NAME = 'sopel-mcmxi'


def lookup_callsign(callsign: str) -> Optional[Dict]:
    """Lookup callsign information from HamDB."""
    callsign = callsign.strip().upper()
    url = f'{HAMDB_API_URL}/{callsign}/json/{APP_NAME}'

    logger.info(f'Looking up callsign: {callsign}')
    response = http.get(url, timeout=10)

    if not response:
        logger.error('Failed to query HamDB API')
        return None

    # Response should be JSON
    if not isinstance(response, dict):
        logger.error('Invalid response format from HamDB API')
        return None

    # Check for errors
    messages = response.get('messages', {})
    status = messages.get('status', '')
    
    if status == 'NOT_FOUND':
        return {'error': 'NOT_FOUND'}
    
    if status and status != 'OK':
        logger.warning(f'HamDB API status: {status}')
        return {'error': status}

    # Get callsign data
    hamdb = response.get('hamdb', {})
    callsign_data = hamdb.get('callsign', {})
    
    if not callsign_data:
        return None

    return callsign_data


@plugin.command('hamdb')
@plugin.example('`hamdb W1AW')
@plugin.example('`hamdb K1ABC')
def hamdb_lookup(bot, trigger):
    """Lookup amateur radio callsign information from HamDB.org."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `hamdb <callsign>')
        bot.notice(trigger.nick, 'Example: `hamdb W1AW')
        return

    callsign = trigger.group(2).strip().upper()

    # Validate callsign format (basic check)
    if not callsign or len(callsign) < 3:
        bot.notice(trigger.nick, 'Invalid callsign format')
        return

    data = lookup_callsign(callsign)

    if not data:
        bot.notice(
            trigger.nick,
            f'No information found for callsign: {callsign}'
        )
        return

    if 'error' in data:
        if data['error'] == 'NOT_FOUND':
            bot.notice(
                trigger.nick,
                f'Callsign {callsign} not found in HamDB database'
            )
        else:
            bot.notice(trigger.nick, f'HamDB API error: {data["error"]}')
        return

    # Display callsign information
    call = data.get('call', callsign)
    bot.say(f"{formatter.bold('Callsign')}: {formatter.monospace(call)}")

    # Name
    fname = data.get('fname', '')
    name = data.get('name', '')
    if fname or name:
        full_name = f"{fname} {name}".strip()
        bot.say(f"{formatter.bold('Name')}: {full_name}")

    # Address
    addr1 = data.get('addr1', '')
    addr2 = data.get('addr2', '')
    city = data.get('city', '')
    state = data.get('state', '')
    zip_code = data.get('zip', '')
    country = data.get('country', '')

    address_parts = []
    if addr1:
        address_parts.append(addr1)
    if addr2:
        address_parts.append(addr2)
    if city:
        address_parts.append(city)
    if state:
        address_parts.append(state)
    if zip_code:
        address_parts.append(zip_code)
    if country:
        address_parts.append(country)

    if address_parts:
        address = ', '.join(address_parts)
        bot.say(f"{formatter.bold('Address')}: {address}")

    # Grid square
    grid = data.get('grid', '')
    if grid:
        bot.say(f"{formatter.bold('Grid')}: {formatter.monospace(grid)}")

    # License class
    class_field = data.get('class', '')
    if class_field:
        bot.say(f"{formatter.bold('Class')}: {class_field}")

    # License expiration
    expires = data.get('expires', '')
    if expires:
        bot.say(f"{formatter.bold('Expires')}: {expires}")

    # Email
    email = data.get('email', '')
    if email:
        bot.say(f"{formatter.bold('Email')}: {email}")

    # Website
    url_field = data.get('url', '')
    if url_field:
        bot.say(f"{formatter.bold('Website')}: {url_field}")

    # Bio
    bio = data.get('bio', '')
    if bio:
        bio_short = bio[:200] + '...' if len(bio) > 200 else bio
        bot.say(f"{formatter.bold('Bio')}: {bio_short}")

    # HamDB page link
    bot.say(f"HamDB: https://hamdb.org/{call}")

