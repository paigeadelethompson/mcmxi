"""
Sopel module for Documents & Productivity APIs.
Supports 4 public APIs with no authentication required.
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


def setup(bot):
    """Module setup - Documents & Productivity APIs loaded."""
    register_apis('documents_productivity', APIS)
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
