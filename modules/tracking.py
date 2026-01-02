"""
Sopel module for Tracking APIs.
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
        'name': 'PostalPinCode',
        'description': 'API for getting Pincode details in India',
        'link': 'http://www.postalpincode.in/Api-Details',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'WhatPulse',
        'description': 'Small application that measures your keyboard/mouse usage',
        'link': 'https://developer.whatpulse.org/#web-api',
        'https': True,
        'cors': 'unknown',
    },
]







def setup(bot):
    """Module setup - Tracking APIs loaded."""
    register_apis('tracking', APIS)
    bot.memory['tracking_loaded'] = True
    bot.memory['tracking_count'] = 2


def shutdown(bot):
    """Module shutdown."""
    bot.memory['tracking_loaded'] = False


@plugin.command('pincode_postalpincode')
@plugin.example('`pincode_postalpincode 110001')
def pincode_postalpincode(bot, trigger):
    """Get Indian postal pincode details using PostalPinCode API."""
    # PostalPinCode: http://www.postalpincode.in/Api-Details
    # Endpoint: GET http://www.postalpincode.in/api/pincode/{pincode}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pincode_postalpincode <pincode>')
        bot.notice(trigger.nick, 'Example: `pincode_postalpincode 110001')
        return

    pincode = trigger.group(2).strip()

    if not pincode.isdigit() or len(pincode) != 6:
        bot.notice(trigger.nick, 'Pincode must be a 6-digit number.')
        return

    logger.info(f'PostalPinCode lookup: {pincode}')

    url = f'http://www.postalpincode.in/api/pincode/{pincode}'

    logger.debug(f'Looking up pincode: {url}')
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to lookup pincode.')
        return

    status = data.get('Status', '')
    if status != 'Success':
        bot.notice(trigger.nick, f'Pincode not found: {pincode}')
        return

    post_offices = data.get('PostOffice', [])
    if not post_offices:
        bot.notice(trigger.nick, f'No post office found for pincode: {pincode}')
        return

    # Get first post office details
    po = post_offices[0]
    name = po.get('Name', 'Unknown')
    district = po.get('District', 'Unknown')
    state = po.get('State', 'Unknown')
    country = po.get('Country', 'India')

    response = f"{formatter.bold('Pincode')} {formatter.monospace(pincode)}"
    response += f" | {formatter.bold(name)}"
    response += f" | District: {formatter.italic(district)}"
    response += f" | State: {formatter.italic(state)}"
    if country != 'India':
        response += f" | Country: {formatter.italic(country)}"

    bot.say(formatter.truncate(response, max_len=400))
