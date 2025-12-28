"""
Sopel module for Programming APIs.
Supports 5 public APIs with no authentication required.
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
        'name': 'JMESPath',
        'description': 'Run JMESPath queries on JSON data for filtering, transforming, and extracting results',
        'link': 'https://noteapiconnector.com/jmespath-free-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Let\'s Count',
        'description': 'Create, retrieve, update, increment, and decrement counters identified by namespace and key',
        'link': 'https://letscountapi.com',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'PHPhub',
        'description': 'PHP syntax checker',
        'link': 'https://phphub.net/linter/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Pythonium',
        'description': 'Validate Python code syntax',
        'link': 'https://pythonium.net/linter',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Softwium',
        'description': 'Validate SQL queries',
        'link': 'https://softwium.com/sql-validator/',
        'https': True,
        'cors': 'no',
    },
]


@plugin.command('programming')
@plugin.command('programming')
@plugin.example(f'.programming')
def programming_list(bot, trigger):
    """List all available Programming APIs."""
    bot.say(f'Available Programming APIs (5):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .programming_info <name> for details')


@plugin.command('programming_info')
@plugin.example(f'.programming_info <name>')
def programming_info(bot, trigger):
    """Get information about a specific Programming API."""
    if not trigger.group(2):
        bot.say(f'Usage: .programming_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('programming_search')
@plugin.example(f'.programming_search <query>')
def programming_search(bot, trigger):
    """Search Programming APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .programming_search <query>')
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
    """Module setup - Programming APIs loaded."""
    bot.memory['programming_loaded'] = True
    bot.memory['programming_count'] = 5


def shutdown(bot):
    """Module shutdown."""
    bot.memory['programming_loaded'] = False


@plugin.command('python_pythonium')
@plugin.example('.python_pythonium print("hello")')
def python_pythonium(bot, trigger):
    """Validate Python code syntax using Pythonium API."""
    # Pythonium: https://pythonium.net/linter
    # Endpoint: POST https://pythonium.net/api/v1/lint
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .python_pythonium <python_code>')
        bot.notice(trigger.nick, 'Example: .python_pythonium print("hello")')
        return
    
    code = trigger.group(2).strip()
    
    if len(code) > 1000:
        bot.notice(trigger.nick, 'Code is too long (max 1000 characters).')
        return
    
    logger.info(f'Pythonium syntax check')
    
    url = 'https://pythonium.net/api/v1/lint'
    post_data = http.urlencode({'code': code})
    
    logger.debug(f'Validating Python code: {url}')
    data = http.post(url, data=post_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    if not data:
        bot.notice(trigger.nick, 'Failed to validate Python code.')
        return
    
    # Check for errors
    errors = data.get('errors', [])
    if not errors:
        bot.say(f'{formatter.bold("Python Syntax")}: {formatter.bold("Valid")} ✓')
    else:
        bot.say(f'{formatter.bold("Python Syntax")}: {formatter.bold("Invalid")} ✗')
        # Show first error
        if len(errors) > 0:
            first_error = errors[0]
            error_msg = first_error.get('message', 'Unknown error')
            line = first_error.get('line', 0)
            bot.say(f'Error on line {formatter.monospace(str(line))}: {formatter.italic(error_msg)}')
