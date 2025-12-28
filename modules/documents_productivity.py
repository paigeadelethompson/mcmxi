"""
Sopel module for Documents & Productivity APIs.
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
        'name': 'FastApi Simple Calculator',
        'description': 'Math, Stadistics, Conversions, Currency and more',
        'link': 'https://fastapi-calculadora.onrender.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'URL to Markdown',
        'description': 'Convert web page to MarkDown',
        'link': 'https://github.com/macsplit/urltomarkdown',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Vector Express v2.0',
        'description': 'Free vector file converting API',
        'link': 'https://vector.express',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'WakaTime',
        'description': 'Automated time tracking leaderboards for programmers',
        'link': 'https://wakatime.com/developers',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('documents_productivity')
@plugin.command('documentsproductivity')
@plugin.example(f'.documents_productivity')
def documents_productivity_list(bot, trigger):
    """List all available Documents & Productivity APIs."""
    bot.say(f'Available Documents & Productivity APIs (4):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .documents_productivity_info <name> for details')


@plugin.command('documents_productivity_info')
@plugin.example(f'.documents_productivity_info <name>')
def documents_productivity_info(bot, trigger):
    """Get information about a specific Documents & Productivity API."""
    if not trigger.group(2):
        bot.say(f'Usage: .documents_productivity_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('documents_productivity_search')
@plugin.example(f'.documents_productivity_search <query>')
def documents_productivity_search(bot, trigger):
    """Search Documents & Productivity APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .documents_productivity_search <query>')
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
    """Module setup - Documents & Productivity APIs loaded."""
    bot.memory['documents_productivity_loaded'] = True
    bot.memory['documents_productivity_count'] = 4


def shutdown(bot):
    """Module shutdown."""
    bot.memory['documents_productivity_loaded'] = False


@plugin.command('calc_fastapi')
@plugin.example('.calc_fastapi 2+2')
def calc_fastapi(bot, trigger):
    """Perform calculations using FastApi Simple Calculator."""
    # FastApi Simple Calculator: https://fastapi-calculadora.onrender.com/
    # Endpoint: GET https://fastapi-calculadora.onrender.com/calculate?expression={expr}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .calc_fastapi <expression>')
        bot.notice(trigger.nick, 'Example: .calc_fastapi 2+2')
        return
    
    expression = trigger.group(2).strip()
    
    logger.info(f'FastAPI calculator: {expression}')
    
    encoded_expr = http.quote(expression)
    url = f'https://fastapi-calculadora.onrender.com/calculate?expression={encoded_expr}'
    
    logger.debug(f'Calculating: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to calculate expression.')
        return
    
    result = data.get('result', data.get('answer', 'Unknown'))
    expression_used = data.get('expression', expression)
    
    response = f"{formatter.bold('Calculator')} {formatter.monospace(expression_used)}"
    response += f" = {formatter.bold(str(result))}"
    bot.say(formatter.truncate(response, max_len=400))
