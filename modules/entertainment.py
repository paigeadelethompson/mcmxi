"""
Sopel module for Entertainment APIs.
Supports 12 public APIs with no authentication required.
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
        'name': 'chucknorris.io',
        'description': 'JSON API for hand curated Chuck Norris jokes',
        'link': 'https://api.chucknorris.io',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Corporate Buzz Words',
        'description': 'REST API for Corporate Buzz Words',
        'link': 'https://github.com/sameerkumar18/corporate-bs-generator-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'elonmu.sh',
        'description': 'Get random news article featuring Elon Musk',
        'link': 'https://elonmu.sh/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Imgflip',
        'description': 'Gets an array of popular memes',
        'link': 'https://imgflip.com/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'JokeAPI',
        'description': 'Jokes in multiple formats',
        'link': 'https://jokeapi.dev/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Keanu Reeves Whoa',
        'description': 'JSON API for every "whoa" said by actor Keanu Reeves in his movies',
        'link': 'https://whoa.onrender.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Meme Maker',
        'description': 'REST API for create your own meme',
        'link': 'https://mememaker.github.io/API/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Official Joke',
        'description': 'API for random and programming jokes',
        'link': 'https://official-joke-api.appspot.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Random Dad Joke',
        'description': 'API for largest selection of dad jokes on the internet',
        'link': 'https://icanhazdadjoke.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Random Useless Facts',
        'description': 'Get useless, but true facts',
        'link': 'https://uselessfacts.jsph.pl/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Techy',
        'description': 'JSON and Plaintext API for tech-savvy sounding phrases',
        'link': 'https://techy-api.vercel.app/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Yo Momma Jokes',
        'description': 'REST API for Yo Momma Jokes',
        'link': 'https://github.com/beanboi7/yomomma-apiv2',
        'https': True,
        'cors': 'unknown',
    },
]







@plugin.command('joke_jokeapi')
@plugin.example('.joke_jokeapi')
@plugin.example('.joke_jokeapi programming')
def joke_jokeapi(bot, trigger):
    """Get a random joke using JokeAPI."""
    category = trigger.group(2).strip().lower() if trigger.group(2) else 'any'

    logger.info(f'Fetching joke (category: {category})')

    # JokeAPI supports categories: any, programming, misc, dark, pun, spooky, christmas
    valid_categories = ['any', 'programming', 'misc', 'dark', 'pun', 'spooky', 'christmas']
    if category not in valid_categories:
        category = 'any'

    # Don't restrict type - allow both single and twopart jokes
    url = f'https://v2.jokeapi.dev/joke/{category}'

    logger.debug(f'Fetching joke: {url}')
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to fetch joke. Please try again.')
        return

    if data.get('error'):
        bot.notice(trigger.nick, f"Error: {data.get('message', 'Unknown error')}")
        return

    # JokeAPI can return single jokes or two-part jokes
    joke_text = ''
    joke_type = data.get('type', '')
    if joke_type == 'single':
        joke_text = data.get('joke', '')
    elif joke_type == 'twopart':
        setup = data.get('setup', '')
        delivery = data.get('delivery', '')
        if setup and delivery:
            joke_text = f"{formatter.italic(setup)} → {formatter.bold(delivery)}"

    category_used = data.get('category', 'any').upper()

    if joke_text:
        response = f"{formatter.bold(f'[{category_used}]')} {joke_text}"
        bot.say(formatter.truncate(response, max_len=400))
    else:
        bot.notice(trigger.nick, 'No joke found.')


def setup(bot):
    """Module setup - Entertainment APIs loaded."""
    register_apis('entertainment', APIS)
    bot.memory['entertainment_loaded'] = True
    bot.memory['entertainment_count'] = 12
    logger.info('Entertainment module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['entertainment_loaded'] = False
    logger.info('Entertainment module unloaded')
