"""
Sopel module for Cloud Storage & File Sharing APIs.
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
        'name': 'Delta Lake',
        'description': 'Open-source storage framework enabling Lakehouse architecture with Spark, PrestoDB, Flink, Trino, Hive, and APIs',
        'link': 'https://docs.delta.io/latest/delta-apidoc.html',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'File.io',
        'description': 'Super simple file sharing, convenient, anonymous and secure',
        'link': 'https://www.file.io',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'The Null Pointer',
        'description': 'No-bullshit file hosting and URL shortening service',
        'link': 'https://0x0.st',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('cloud_storage_file_sharing')
@plugin.command('cloudstoragefilesharing')
@plugin.example(f'.cloud_storage_file_sharing')
def cloud_storage_file_sharing_list(bot, trigger):
    """List all available Cloud Storage & File Sharing APIs."""
    bot.say(f'Available Cloud Storage & File Sharing APIs (3):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .cloud_storage_file_sharing_info <name> for details')


@plugin.command('cloud_storage_file_sharing_info')
@plugin.example(f'.cloud_storage_file_sharing_info <name>')
def cloud_storage_file_sharing_info(bot, trigger):
    """Get information about a specific Cloud Storage & File Sharing API."""
    if not trigger.group(2):
        bot.say(f'Usage: .cloud_storage_file_sharing_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('cloud_storage_file_sharing_search')
@plugin.example(f'.cloud_storage_file_sharing_search <query>')
def cloud_storage_file_sharing_search(bot, trigger):
    """Search Cloud Storage & File Sharing APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .cloud_storage_file_sharing_search <query>')
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
    """Module setup - Cloud Storage & File Sharing APIs loaded."""
    bot.memory['cloud_storage_file_sharing_loaded'] = True
    bot.memory['cloud_storage_file_sharing_count'] = 3


def shutdown(bot):
    """Module shutdown."""
    bot.memory['cloud_storage_file_sharing_loaded'] = False


@plugin.command('file_0x0')
@plugin.example('.file_0x0 https://example.com/file.txt')
def file_0x0(bot, trigger):
    """Get information about 0x0.st file hosting service."""
    # The Null Pointer: https://0x0.st
    # Note: This is a file upload service, so we'll just show info about it
    
    bot.say(f"{formatter.bold('0x0.st')}: No-bullshit file hosting and URL shortening")
    bot.say(f"Upload endpoint: {formatter.monospace('https://0x0.st/')}")
    bot.notice(trigger.nick, 'Note: File uploads require POST with multipart/form-data. Use curl or web interface.')
