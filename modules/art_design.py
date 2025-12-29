"""
Sopel module for Art & Design APIs.
Supports 13 public APIs with no authentication required.
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
        'name': 'Art Institute of Chicago',
        'description': 'Art',
        'link': 'https://api.artic.edu/docs/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'ColorMagic',
        'description': 'Color Palette Generator',
        'link': 'https://colormagic.app/api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Colormind',
        'description': 'Color scheme generator',
        'link': 'http://colormind.io/api-access/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'ColourLovers',
        'description': 'Get various patterns, palettes and images',
        'link': 'http://www.colourlovers.com/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'EmojiHub',
        'description': 'Get emojis by categories and groups',
        'link': 'https://github.com/cheatsnake/emojihub',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Icon Horse',
        'description': 'Favicons for any website, with fallbacks',
        'link': 'https://icon.horse/usage',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Icons8',
        'description': 'Icons (find "search icon" hyperlink in page)',
        'link': 'https://img.icons8.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Logotypes',
        'description': 'Logotypes of the world in multiples format',
        'link': 'https://logotypes.dev/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Lordicon',
        'description': 'Icons with predone Animations',
        'link': 'https://lordicon.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Metropolitan Museum of Art',
        'description': 'Met Museum of Art',
        'link': 'https://metmuseum.github.io/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'PHP-Noise',
        'description': 'Noise Background Image Generator',
        'link': 'https://php-noise.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'The Color',
        'description': 'Swiss army knife for color',
        'link': 'https://www.thecolorapi.com/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'xColors',
        'description': 'Generate & convert colors',
        'link': 'https://github.com/cheatsnake/xColors-api',
        'https': True,
        'cors': 'yes',
    },
]


@plugin.command('emoji_emojihub')
@plugin.example('.emoji_emojihub random')
@plugin.example('.emoji_emojihub smileys_emotion')
def emoji_emojihub(bot, trigger):
    """Get emojis by category using EmojiHub API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .emoji_emojihub <category> or .emoji_emojihub random')
        bot.notice(trigger.nick, 'Categories: smileys_emotion, people_body, animals_nature, food_drink, travel_places, activities, objects, symbols, flags')
        return

    category = trigger.group(2).strip().lower()
    logger.info(f'Emoji lookup: {category}')

    if category == 'random':
        url = 'https://emojihub.yurace.pro/api/random'
    else:
        encoded_category = http.quote(category)
        url = f'https://emojihub.yurace.pro/api/category/{encoded_category}'

    logger.debug(f'Fetching emoji: {url}')
    data = http.get(url)

    if not data:
        if category == 'random':
            bot.notice(trigger.nick, 'Failed to fetch random emoji. Please try again.')
        else:
            bot.notice(trigger.nick, f'Category "{category}" not found or API error.')
        return

    # API can return single object or array
    emojis = data if isinstance(data, list) else [data]
    emojis = emojis[:3]  # Limit to 3

    if not emojis:
        bot.notice(trigger.nick, 'No emojis found.')
        return

    bot.say(f'Found {len(emojis)} emoji(s):')
    for emoji in emojis:
        name = emoji.get('name', 'Unknown')
        emoji_char = emoji.get('htmlCode', [''])[0] if emoji.get('htmlCode') else ''
        category_used = emoji.get('category', 'Unknown')
        group = emoji.get('group', 'Unknown')

        response = f"{emoji_char} {formatter.bold(name)}"
        if category_used != 'Unknown':
            response += f" | Category: {formatter.italic(category_used)}"
        if group != 'Unknown':
            response += f" | Group: {formatter.monospace(group)}"

        bot.say(formatter.truncate(response, max_len=400))

def setup(bot):
    """Module setup - Art & Design APIs loaded."""
    register_apis('art_design', APIS)
    bot.memory['art_design_loaded'] = True
    bot.memory['art_design_count'] = 13
    logger.info('Art & Design module loaded')

def shutdown(bot):
    """Module shutdown."""
    bot.memory['art_design_loaded'] = False
    logger.info('Art & Design module unloaded')
