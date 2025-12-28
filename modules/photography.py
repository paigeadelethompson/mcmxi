"""
Sopel module for Photography APIs.
Supports 4 public APIs with no authentication required.
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
        'name': 'Lorem Picsum',
        'description': 'Images from Unsplash',
        'link': 'https://picsum.photos/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'PlaceKeanu',
        'description': 'Resizable Keanu Reeves placeholder images with grayscale and young Keanu options',
        'link': 'https://placekeanu.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Readme typing SVG',
        'description': 'Customizable typing and deleting text SVG',
        'link': 'https://github.com/DenverCoder1/readme-typing-svg',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'ReSmush.it',
        'description': 'Photo optimization',
        'link': 'https://resmush.it/api',
        'https': False,
        'cors': 'unknown',
    },
]


@plugin.command('photography')
@plugin.command('photography')
@plugin.example(f'.photography')
def photography_list(bot, trigger):
    """List all available Photography APIs."""
    bot.say(f'Available Photography APIs (4):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .photography_info <name> for details')


@plugin.command('photography_info')
@plugin.example(f'.photography_info <name>')
def photography_info(bot, trigger):
    """Get information about a specific Photography API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .photography_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('photography_search')
@plugin.example(f'.photography_search <query>')
def photography_search(bot, trigger):
    """Search Photography APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .photography_search <query>')
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


@plugin.command('image_lorempicsum')
@plugin.example('.image_lorempicsum')
@plugin.example('.image_lorempicsum 800')
def image_lorempicsum(bot, trigger):
    """Get random placeholder image using Lorem Picsum API."""
    size = trigger.group(2).strip() if trigger.group(2) else None
    
    logger.info(f'Lorem Picsum image request: size={size or "random"}')
    
    if size:
        # Try to parse size (can be "800" or "800/600")
        try:
            if '/' in size:
                width, height = size.split('/')
                width = int(width)
                height = int(height)
                url = f'https://picsum.photos/{width}/{height}'
            else:
                width = int(size)
                url = f'https://picsum.photos/{width}'
        except ValueError:
            bot.notice(trigger.nick, 'Invalid size format. Use: <width> or <width>/<height>')
            return
    else:
        # Random image
        url = 'https://picsum.photos/800/600'
    
    # Get image info (not the image itself)
    info_url = url.replace('/photos/', '/id/') + '/info'
    logger.debug(f'Fetching image info: {info_url}')
    data = http.get(info_url)
    
    if not data:
        # If info fails, just return the image URL
        response = f"Random image: {url}"
        bot.say(formatter.truncate(response, max_len=400))
        return
    
    author = data.get('author', 'Unknown')
    width = data.get('width', 'Unknown')
    height = data.get('height', 'Unknown')
    download_url = data.get('download_url', url)
    
    response = f"Image: {formatter.bold(f'{width}x{height}')} | Author: {formatter.italic(author)} | {formatter.monospace(download_url)}"
    bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Photography APIs loaded."""
    bot.memory['photography_loaded'] = True
    bot.memory['photography_count'] = 4
    logger.info('Photography module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['photography_loaded'] = False
    logger.info('Photography module unloaded')
