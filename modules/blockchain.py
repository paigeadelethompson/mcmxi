"""
Sopel module for Blockchain APIs.
Supports 3 public APIs with no authentication required.
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
        'name': 'Chainlink',
        'description': 'Build hybrid smart contracts with Chainlink',
        'link': 'https://chain.link/developer-resources',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Chainpoint',
        'description': 'Chainpoint is a global network for anchoring data to the Bitcoin blockchain',
        'link': 'https://tierion.com/chainpoint/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Steem',
        'description': 'Blockchain-based blogging and social media website',
        'link': 'https://developers.steem.io/',
        'https': False,
        'cors': 'no',
    },
]


@plugin.command('blockchain')
@plugin.command('blockchain')
@plugin.example(f'.blockchain')
def blockchain_list(bot, trigger):
    """List all available Blockchain APIs."""
    bot.say(f'Available Blockchain APIs (3):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .blockchain_info <name> for details')


@plugin.command('blockchain_info')
@plugin.example(f'.blockchain_info <name>')
def blockchain_info(bot, trigger):
    """Get information about a specific Blockchain API."""
    if not trigger.group(2):
        bot.say(f'Usage: .blockchain_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('blockchain_search')
@plugin.example(f'.blockchain_search <query>')
def blockchain_search(bot, trigger):
    """Search Blockchain APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .blockchain_search <query>')
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
    """Module setup - Blockchain APIs loaded."""
    bot.memory['blockchain_loaded'] = True
    bot.memory['blockchain_count'] = 3


def shutdown(bot):
    """Module shutdown."""
    bot.memory['blockchain_loaded'] = False


@plugin.command('chainpoint_info')
@plugin.example('.chainpoint_info')
def chainpoint_info(bot, trigger):
    """Get information about Chainpoint service."""
    # Chainpoint: https://tierion.com/chainpoint/
    # Note: Chainpoint is a service for anchoring data to Bitcoin blockchain
    # Full API requires authentication, so we'll show service info
    
    bot.say(f"{formatter.bold('Chainpoint')}: Global network for anchoring data to Bitcoin blockchain")
    bot.say(f"Service: {formatter.monospace('https://tierion.com/chainpoint/')}")
    bot.notice(trigger.nick, 'Note: Full Chainpoint API requires authentication. Visit the website for API access.')
