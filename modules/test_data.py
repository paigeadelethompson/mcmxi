"""
Sopel module for Test Data APIs.
Supports 19 public APIs with no authentication required.
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
        'name': 'Bacon Ipsum',
        'description': 'A Meatier Lorem Ipsum Generator',
        'link': 'https://baconipsum.com/json-api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Dicebear Avatars',
        'description': 'Generate random pixel-art avatars',
        'link': 'https://avatars.dicebear.com/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Faker',
        'description': 'Generate massive amounts of fake (but realistic) data for testing and development.',
        'link': 'https://fakerjs.dev/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'FakerAPI',
        'description': 'APIs collection to get fake data',
        'link': 'https://fakerapi.it/en',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'FakeStoreAPI',
        'description': 'Fake store rest API for your e-commerce or shopping website prototype',
        'link': 'https://fakestoreapi.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'ItsThisForThat',
        'description': 'Generate Random startup ideas',
        'link': 'https://itsthisforthat.com/api.php',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'JSONing',
        'description': 'Fake REST API for prototyping',
        'link': 'https://jsoning.com/api/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'JSONPlaceholder',
        'description': 'Fake data for testing and prototyping',
        'link': 'http://jsonplaceholder.typicode.com/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Loripsum',
        'description': "The \"lorem ipsum\" generator that doesn't suck",
        'link': 'http://loripsum.net/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Metaphorsum',
        'description': 'Generate demo paragraphs giving number of words and sentences',
        'link': 'http://metaphorpsum.com/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Mockae',
        'description': 'Fake REST API powered by Lua',
        'link': 'https://mockae.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'QuickMocker',
        'description': 'API mocking tool to generate contextual, fake or random data',
        'link': 'https://quickmocker.com',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Random Data',
        'description': 'Random data generator',
        'link': 'https://random-data-api.com',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'RandomUser',
        'description': 'Generates and list user data',
        'link': 'https://randomuser.me',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'RoboHash',
        'description': 'Generate random robot/alien avatars',
        'link': 'https://robohash.org/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'This Person Does not Exist',
        'description': 'Generates real-life faces of people who do not exist',
        'link': 'https://thispersondoesnotexist.com',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'UUID Generator',
        'description': 'Generate UUIDs',
        'link': 'https://www.uuidtools.com/docs',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'What The Commit',
        'description': 'Random commit message generator',
        'link': 'http://whatthecommit.com/index.txt',
        'https': False,
        'cors': 'yes',
    },
    {
        'name': 'Yes No',
        'description': 'Generate yes or no randomly',
        'link': 'https://yesno.wtf/api',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('test_data')
@plugin.command('testdata')
@plugin.example(f'.test_data')
def test_data_list(bot, trigger):
    """List all available Test Data APIs."""
    bot.say(f'Available Test Data APIs (19):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .test_data_info <name> for details')


@plugin.command('test_data_info')
@plugin.example(f'.test_data_info <name>')
def test_data_info(bot, trigger):
    """Get information about a specific Test Data API."""
    if not trigger.group(2):
        bot.say(f'Usage: .test_data_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('test_data_search')
@plugin.example(f'.test_data_search <query>')
def test_data_search(bot, trigger):
    """Search Test Data APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .test_data_search <query>')
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
    """Module setup - Test Data APIs loaded."""
    bot.memory['test_data_loaded'] = True
    bot.memory['test_data_count'] = 19


def shutdown(bot):
    """Module shutdown."""
    bot.memory['test_data_loaded'] = False


@plugin.command('lorem_baconipsum')
@plugin.example('.lorem_baconipsum')
@plugin.example('.lorem_baconipsum 3')
def lorem_baconipsum(bot, trigger):
    """Generate bacon ipsum lorem text using Bacon Ipsum API."""
    # Bacon Ipsum: https://baconipsum.com/json-api/
    # Endpoint: GET https://baconipsum.com/api/?type=all-meat&paras=3&start-with-lorem=1&format=json
    
    paras = 2  # default
    if trigger.group(2):
        try:
            paras = int(trigger.group(2).strip())
            if paras < 1 or paras > 5:
                bot.notice(trigger.nick, 'Paragraphs must be between 1 and 5.')
                return
        except ValueError:
            bot.notice(trigger.nick, 'Invalid number. Please provide a number between 1-5.')
            return
    
    logger.info(f'Bacon Ipsum generation: {paras} paragraphs')
    
    url = f'https://baconipsum.com/api/?type=all-meat&paras={paras}&start-with-lorem=1&format=json'
    
    logger.debug(f'Generating bacon ipsum: {url}')
    data = http.get(url)
    
    if not data or not isinstance(data, list):
        bot.notice(trigger.nick, 'Failed to generate bacon ipsum text.')
        return
    
    bot.say(f'{formatter.bold("Bacon Ipsum")} ({paras} paragraph(s)):')
    for i, para in enumerate(data[:3], 1):
        para_text = para[:200] if isinstance(para, str) else str(para)[:200]
        bot.say(f"{i}. {formatter.italic(para_text)}...")


@plugin.command('avatar_dicebear')
@plugin.example('.avatar_dicebear')
@plugin.example('.avatar_dicebear avataaars')
def avatar_dicebear(bot, trigger):
    """Generate random pixel-art avatar URL using Dicebear Avatars."""
    # Dicebear Avatars: https://avatars.dicebear.com/
    # Endpoint: GET https://api.dicebear.com/7.x/{style}/svg?seed={seed}
    
    style = trigger.group(2).strip() if trigger.group(2) else 'avataaars'
    
    # Validate style (common ones: avataaars, bottts, identicon, initials, pixel-art)
    valid_styles = ['avataaars', 'bottts', 'identicon', 'initials', 'pixel-art', 'personas', 'micah']
    if style not in valid_styles:
        style = 'avataaars'
    
    logger.info(f'Dicebear avatar: {style}')
    
    # Generate random seed
    import random
    seed = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
    
    url = f'https://api.dicebear.com/7.x/{http.quote(style)}/svg?seed={seed}'
    
    bot.say(f"{formatter.bold('Dicebear Avatar')} ({formatter.monospace(style)}): {formatter.monospace(url)}")
