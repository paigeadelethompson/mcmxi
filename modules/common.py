"""
Utility modules for Sopel bot - logger, HTTP client, formatting, permissions, XML parsing.
"""
from sopel.tools import get_logger

# Note: This module is both a utility module (imported by others)
# and a Sopel plugin (provides centralized API registry commands)

# Logger utility
def get_module_logger(name: str):
    """Get a logger for a module."""
    return get_logger(name)


# Import all utilities from split modules
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_registry import (
    api_info_command,
    api_search_command,
    apis_list_command,
    get_apis,
    register_apis,
)
from graphql_client import GraphQLClient
from http_client import CustomHTTPSHandler, HTTPClient
from irc_formatter import IRCFormatter
from opengraph import OpenGraphExtractor
from permissions import Permissions
from xml_parser import XMLParser

# Re-export everything for backward compatibility
__all__ = [
    'get_module_logger',
    'HTTPClient',
    'CustomHTTPSHandler',
    'IRCFormatter',
    'Permissions',
    'XMLParser',
    'GraphQLClient',
    'OpenGraphExtractor',
    'register_apis',
    'get_apis',
]

# Register API registry plugin commands
# Note: api_registry.py defines the command functions, but they need to be registered
# here since common.py is the Sopel-loaded module
from sopel import plugin


@plugin.command('apis')
@plugin.example('.apis')
@plugin.example('.apis animals')
def apis_list(bot, trigger):
    """List all registered API categories or APIs in a specific category."""
    apis_list_command(bot, trigger)


@plugin.command('api_info')
@plugin.example('.api_info animals cat')
def api_info_cmd(bot, trigger):
    """Get information about a specific API. Usage: .api_info <category> <api_name>"""
    api_info_command(bot, trigger)


@plugin.command('api_search')
@plugin.example('.api_search animals cat')
def api_search_cmd(bot, trigger):
    """Search APIs by name or description. Usage: .api_search <category> <query>"""
    api_search_command(bot, trigger)
