"""
Sopel module for Food & Drink APIs.
Supports 11 public APIs with no authentication required.
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
        'name': 'BaconMockup',
        'description': 'Resizable bacon placeholder images',
        'link': 'https://baconmockup.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Coffee',
        'description': 'Random pictures of coffee',
        'link': 'https://coffee.alexflipnote.dev/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Foodish',
        'description': 'Random pictures of food dishes',
        'link': 'https://github.com/surhud004/Foodish#readme',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Jelly Belly Wiki',
        'description': 'Data about Jelly Belly beans- flavores, facts, history and more endpoints',
        'link': 'https://jelly-belly-wiki.netlify.app/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Open Brewery DB',
        'description': 'Breweries, Cideries and Craft Beer Bottle Shops',
        'link': 'https://www.openbrewerydb.org',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Open Food Facts',
        'description': 'Food Products Database',
        'link': 'https://world.openfoodfacts.org/data',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'PunkAPI',
        'description': "BrewDog\'s DIY Dog beer catalogue as an API",
        'link': 'https://github.com/alxiw/punkapi',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Status Pizza',
        'description': 'Pizza for every HTTP Status',
        'link': 'https://status.pizza',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'TacoFancy',
        'description': 'Community-driven taco database',
        'link': 'https://github.com/evz/tacofancy-api',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'The Report of the Week',
        'description': 'Food & Drink Reviews',
        'link': 'https://github.com/andyklimczak/TheReportOfTheWeek-API',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'WhiskyHunter',
        'description': 'Past online whisky auctions statistical data',
        'link': 'https://whiskyhunter.net/api/',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('brewery_openbrewery')
@plugin.example('`brewery_openbrewery seattle')
@plugin.example('`brewery_openbrewery 5494')
def brewery_openbrewery(bot, trigger):
    """Search for breweries using Open Brewery DB API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `brewery_openbrewery <city/name> or .brewery_openbrewery <brewery_id>')
        return

    query = trigger.group(2).strip()
    logger.info(f'Brewery search: {query}')

    # Check if it's a numeric ID
    if query.isdigit():
        get_brewery_by_id(bot, trigger.nick, int(query))
    else:
        search_breweries(bot, trigger.nick, query)


def search_breweries(bot, nick: str, query: str):
    """Search for breweries by name or city."""
    encoded_query = http.quote(query)
    url = f'https://api.openbrewerydb.org/v1/breweries?by_name={encoded_query}&per_page=3'

    logger.debug(f'Searching breweries: {url}')
    data = http.get(url)

    if not data:
        # Try city search if name search fails
        url = f'https://api.openbrewerydb.org/v1/breweries?by_city={encoded_query}&per_page=3'
        data = http.get(url)

    if not data or not isinstance(data, list):
        bot.notice(nick, 'No breweries found or API error. Please try again.')
        return

    results = data[:3]

    if not results:
        bot.notice(nick, f'No breweries found for "{query}"')
        return

    bot.say(f'Found {len(results)} brewery(ies) for "{query}":')
    for brewery in results:
        name = brewery.get('name', 'Unknown')
        city = brewery.get('city', '')
        state = brewery.get('state', '')
        brewery_type = brewery.get('brewery_type', '')
        brewery_id = brewery.get('id', '')

        response = f"{formatter.bold(name)}"
        if city and state:
            response += f" - {formatter.italic(f'{city}, {state}')}"
        if brewery_type:
            response += f" {formatter.monospace(f'({brewery_type})')}"
        if brewery_id:
            response += f" | ID: {formatter.monospace(str(brewery_id))}"

        bot.say(formatter.truncate(response, max_len=400))


def get_brewery_by_id(bot, nick: str, brewery_id: int):
    """Get brewery details by ID."""
    url = f'https://api.openbrewerydb.org/v1/breweries/{brewery_id}'

    logger.debug(f'Fetching brewery by ID: {url}')
    data = http.get(url)

    if not data:
        bot.notice(nick, f'Brewery with ID {brewery_id} not found.')
        return

    name = data.get('name', 'Unknown')
    city = data.get('city', '')
    state = data.get('state', '')
    brewery_type = data.get('brewery_type', '')
    website = data.get('website_url', '')
    phone = data.get('phone', '')

    response = f"{formatter.bold(name)}"
    if city and state:
        response += f" - {formatter.italic(f'{city}, {state}')}"
    if brewery_type:
        response += f" | Type: {formatter.monospace(brewery_type)}"
    if website:
        response += f" | {formatter.monospace(website)}"
    if phone:
        response += f" | {formatter.monospace(phone)}"

    bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Food & Drink APIs loaded."""
    register_apis('food_drink', APIS)
    bot.memory['food_drink_loaded'] = True
    bot.memory['food_drink_count'] = 11
    logger.info('Food & Drink module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['food_drink_loaded'] = False
    logger.info('Food & Drink module unloaded')
