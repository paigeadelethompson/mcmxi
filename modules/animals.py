"""
Sopel module for Animals APIs.
Supports 16 public APIs with no authentication required.
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
        'name': 'Cat Facts',
        'description': 'Daily cat facts',
        'link': 'https://alexwohlbruck.github.io/cat-facts/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Cataas',
        'description': 'Cat as a service (cats pictures and gifs)',
        'link': 'https://cataas.com/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Dog Pics',
        'description': 'Pictures of dogs based on the Stanford Dogs Dataset',
        'link': 'https://dog.ceo/dog-api/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Dogs',
        'description': 'Random facts and breed information about dogs',
        'link': 'https://dogapi.dog/docs/api-v2',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'HTTP Cat',
        'description': 'Cat for every HTTP Status',
        'link': 'https://http.cat/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'HTTP Dog',
        'description': 'Dogs for every HTTP response status code',
        'link': 'https://http.dog/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'MeowFacts',
        'description': 'Get random cat facts',
        'link': 'https://github.com/wh-iterabb-it/meowfacts',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Movebank',
        'description': 'Movement and Migration data of animals',
        'link': 'https://github.com/movebank/movebank-api-doc',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'PlaceBear',
        'description': 'Placeholder bear pictures',
        'link': 'https://placebear.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'PlaceDog',
        'description': 'Placeholder Dog pictures',
        'link': 'https://place.dog',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'RandomDog',
        'description': 'Random pictures of dogs',
        'link': 'https://random.dog/woof.json',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'RandomDuck',
        'description': 'Random pictures of ducks',
        'link': 'https://random-d.uk/api',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'RandomFox',
        'description': 'Random pictures of foxes',
        'link': 'https://randomfox.ca/floof/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'RescueGroups',
        'description': 'Adoption',
        'link': 'https://userguide.rescuegroups.org/display/APIDG/API+Developers+Guide+Home',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'WoRMS',
        'description': 'Authoritative list of marine species names and taxonomy',
        'link': 'https://www.marinespecies.org/rest/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'xeno-canto',
        'description': 'Bird recordings',
        'link': 'https://xeno-canto.org/explore/api',
        'https': True,
        'cors': 'yes',
    },
]


@plugin.command('animals')
@plugin.command('animals')
@plugin.example(f'.animals')
def animals_list(bot, trigger):
    """List all available Animals APIs."""
    bot.say(f'Available Animals APIs (16):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .animals_info <name> for details')


@plugin.command('animals_info')
@plugin.example(f'.animals_info <name>')
def animals_info(bot, trigger):
    """Get information about a specific Animals API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .animals_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('animals_search')
@plugin.example(f'.animals_search <query>')
def animals_search(bot, trigger):
    """Search Animals APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .animals_search <query>')
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


@plugin.command('dog_dogceo')
@plugin.example('.dog_dogceo')
@plugin.example('.dog_dogceo hound')
def dog_dogceo(bot, trigger):
    """Get random dog picture or by breed using Dog CEO API."""
    breed = trigger.group(2).strip().lower() if trigger.group(2) else None
    
    logger.info(f'Dog API request: breed={breed or "random"}')
    
    if breed:
        # Get random image by breed
        encoded_breed = http.quote(breed)
        url = f'https://dog.ceo/api/breed/{encoded_breed}/images/random'
    else:
        # Get random dog image
        url = 'https://dog.ceo/api/breeds/image/random'
    
    logger.debug(f'Fetching dog image: {url}')
    data = http.get(url)
    
    if not data or data.get('status') != 'success':
        if breed:
            bot.notice(trigger.nick, f'Breed "{breed}" not found or API error.')
        else:
            bot.notice(trigger.nick, 'Failed to fetch dog image. Please try again.')
        return
    
    image_url = data.get('message', '')
    if image_url:
        # Extract breed from URL if available
        breed_from_url = image_url.split('/breeds/')[-1].split('/')[0] if '/breeds/' in image_url else None
        if breed_from_url:
            breed_display = breed_from_url.replace('-', ' ').title()
            response = f"{formatter.bold(breed_display)} dog: {formatter.monospace(image_url)}"
        else:
            response = f"{formatter.bold('Random dog')}: {formatter.monospace(image_url)}"
        bot.say(formatter.truncate(response, max_len=400))
    else:
        bot.notice(trigger.nick, 'No image URL in response.')


def setup(bot):
    """Module setup - Animals APIs loaded."""
    bot.memory['animals_loaded'] = True
    bot.memory['animals_count'] = 16
    logger.info('Animals module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['animals_loaded'] = False
    logger.info('Animals module unloaded')
