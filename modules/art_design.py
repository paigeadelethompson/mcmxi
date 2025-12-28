"""
Sopel module for Art & Design APIs.
Supports 13 public APIs with no authentication required.
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


@plugin.command('art_design')
@plugin.command('artdesign')
@plugin.example(f'.art_design')
def art_design_list(bot, trigger):
    """List all available Art & Design APIs."""
    bot.say(f'Available Art & Design APIs (13):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .art_design_info <name> for details')


@plugin.command('art_design_info')
@plugin.example(f'.art_design_info <name>')
def art_design_info(bot, trigger):
    """Get information about a specific Art & Design API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .art_design_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('art_design_search')
@plugin.example(f'.art_design_search <query>')
def art_design_search(bot, trigger):
    """Search Art & Design APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .art_design_search <query>')
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


@plugin.command('emoji_emojihub')
@plugin.example('.emoji_emojihub smile')
@plugin.example('.emoji_emojihub random')
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
    bot.memory['art_design_loaded'] = True
    bot.memory['art_design_count'] = 13
    logger.info('Art & Design module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['art_design_loaded'] = False
    logger.info('Art & Design module unloaded')
