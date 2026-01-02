"""
Sopel module for Cloud Storage & File Sharing APIs.
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

def setup(bot):
    """Module setup - Cloud Storage & File Sharing APIs loaded."""
    register_apis('cloud_storage_file_sharing', APIS)
    bot.memory['cloud_storage_file_sharing_loaded'] = True
    bot.memory['cloud_storage_file_sharing_count'] = 3

def shutdown(bot):
    """Module shutdown."""
    bot.memory['cloud_storage_file_sharing_loaded'] = False

@plugin.command('file_0x0')
@plugin.example('`file_0x0 https://example.com/file.txt')
def file_0x0(bot, trigger):
    """Get information about 0x0.st file hosting service."""
    # The Null Pointer: https://0x0.st
    # Note: This is a file upload service, so we'll just show info about it

    bot.say(f"{formatter.bold('0x0.st')}: No-bullshit file hosting and URL shortening")
    bot.say(f"Upload endpoint: {formatter.monospace('https://0x0.st/')}")
    bot.notice(trigger.nick, 'Note: File uploads require POST with multipart/form-data. Use curl or web interface.')
