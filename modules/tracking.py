"""
Sopel module for Tracking APIs.
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


@plugin.command('tracking')
@plugin.command('tracking')
@plugin.example(f'.tracking')
def tracking_list(bot, trigger):
    """List all available Tracking APIs."""
    bot.say(f'Available Tracking APIs (2):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .tracking_info <name> for details')


@plugin.command('tracking_info')
@plugin.example(f'.tracking_info <name>')
def tracking_info(bot, trigger):
    """Get information about a specific Tracking API."""
    if not trigger.group(2):
        bot.say(f'Usage: .tracking_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('tracking_search')
@plugin.example(f'.tracking_search <query>')
def tracking_search(bot, trigger):
    """Search Tracking APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .tracking_search <query>')
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
    """Module setup - Tracking APIs loaded."""
    bot.memory['tracking_loaded'] = True
    bot.memory['tracking_count'] = 2


def shutdown(bot):
    """Module shutdown."""
    bot.memory['tracking_loaded'] = False


@plugin.command('pincode_postalpincode')
@plugin.example('.pincode_postalpincode 110001')
def pincode_postalpincode(bot, trigger):
    """Get Indian postal pincode details using PostalPinCode API."""
    # PostalPinCode: http://www.postalpincode.in/Api-Details
    # Endpoint: GET http://www.postalpincode.in/api/pincode/{pincode}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .pincode_postalpincode <pincode>')
        bot.notice(trigger.nick, 'Example: .pincode_postalpincode 110001')
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
