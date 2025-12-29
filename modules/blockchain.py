"""
Sopel module for Blockchain APIs.
Supports 3 public APIs with no authentication required.
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




def setup(bot):
    """Module setup - Blockchain APIs loaded."""
    register_apis('blockchain', APIS)
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
