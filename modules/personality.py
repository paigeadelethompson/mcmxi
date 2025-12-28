"""
Sopel module for Personality APIs.
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
        'name': 'Advice Slip',
        'description': 'Generate random advice slips',
        'link': 'http://api.adviceslip.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'akshaykumar-rest',
        'description': 'Akshay Kumar for every HTTP status code',
        'link': 'https://akshaykumar-rest.vercel.app/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Forismatic',
        'description': 'Inspirational Quotes',
        'link': 'http://forismatic.com/en/api/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Joke Father',
        'description': 'Ultimate collection of dad jokes',
        'link': 'https://jokefather.com/api/jokes/random',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'icanhazdadjoke',
        'description': 'The largest selection of dad jokes on the internet',
        'link': 'https://icanhazdadjoke.com/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Indian Quotes',
        'description': "Curated quotes from India\'s most successful entrepreneurs",
        'link': 'https://indian-quotes-api.vercel.app/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'kanye.rest',
        'description': 'REST API for random Kanye West quotes',
        'link': 'https://kanye.rest',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'kimiquotes',
        'description': 'Team radio and interview quotes by Finnish F1 legend Kimi Räikkönen',
        'link': 'https://kimiquotes.pages.dev/docs',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Programming Quotes',
        'description': 'Programming Quotes API for open source projects',
        'link': 'https://github.com/skolakoda/programming-quotes-api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Quotable Quotes',
        'description': 'Quotable is a free, open source quotations API',
        'link': 'https://github.com/lukePeavey/quotable',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Quote Garden',
        'description': 'REST API for more than 5000 famous quotes',
        'link': 'https://pprathameshmore.github.io/QuoteGarden/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Quoterism',
        'description': "The Web\'s Largest Collection of Human Inspiration",
        'link': 'https://www.quoterism.com/developer',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Quotes on Design',
        'description': 'Inspirational Quotes',
        'link': 'https://quotesondesign.com/api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Stoicism Quote',
        'description': 'Quotes about Stoicism',
        'link': 'https://github.com/tlcheah2/stoic-quote-lambda-public-api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'They Said So Quotes',
        'description': 'Quotes Trusted by many fortune brands around the world',
        'link': 'https://theysaidso.com/api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Traitify',
        'description': 'Assess, collect and analyze Personality',
        'link': 'https://app.traitify.com/developer',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Vadivelu HTTP Codes',
        'description': 'On demand HTTP Codes with images',
        'link': 'https://vadivelu.anoram.com/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'WhoIsTheOldest',
        'description': 'This application tracks and displays data about the oldest person currently alive and the oldest person ever recorded.',
        'link': 'https://whoistheoldest.com',
        'https': False,
        'cors': 'no',
    },
    {
        'name': 'Zen Quotes',
        'description': 'Large collection of Zen quotes for inspiration',
        'link': 'https://zenquotes.io/',
        'https': True,
        'cors': 'yes',
    },
]


@plugin.command('personality')
@plugin.command('personality')
@plugin.example(f'.personality')
def personality_list(bot, trigger):
    """List all available Personality APIs."""
    bot.say(f'Available Personality APIs (19):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .personality_info <name> for details')


@plugin.command('personality_info')
@plugin.example(f'.personality_info <name>')
def personality_info(bot, trigger):
    """Get information about a specific Personality API."""
    if not trigger.group(2):
        bot.say(f'Usage: .personality_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('personality_search')
@plugin.example(f'.personality_search <query>')
def personality_search(bot, trigger):
    """Search Personality APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .personality_search <query>')
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
    """Module setup - Personality APIs loaded."""
    bot.memory['personality_loaded'] = True
    bot.memory['personality_count'] = 19


def shutdown(bot):
    """Module shutdown."""
    bot.memory['personality_loaded'] = False


@plugin.command('quote_adviceslip')
@plugin.example('.quote_adviceslip')
def quote_adviceslip(bot, trigger):
    """Get random advice from Advice Slip API."""
    # Advice Slip: http://api.adviceslip.com/
    # Endpoint: GET https://api.adviceslip.com/advice
    
    logger.info('Advice Slip quote lookup')
    
    url = 'https://api.adviceslip.com/advice'
    
    logger.debug(f'Fetching advice: {url}')
    data = http.get(url)
    
    if not data or 'slip' not in data:
        bot.notice(trigger.nick, 'Failed to fetch advice.')
        return
    
    slip = data.get('slip', {})
    advice = slip.get('advice', '')
    
    if advice:
        bot.say(f"{formatter.italic(advice)}")
