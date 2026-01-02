"""
Sopel module for Patent APIs.
Supports 2 public APIs with no authentication required.
"""

import json
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
        'name': 'PatentsView ',
        'description': 'API is intended to explore and visualize trends/patterns across the US innovation landscape',
        'link': 'https://patentsview.org/apis/purpose',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'USPTO',
        'description': 'USA patent api services',
        'link': 'https://www.uspto.gov/learning-and-resources/open-data-and-mobility',
        'https': True,
        'cors': 'unknown',
    },
]




def setup(bot):
    """Module setup - Patent APIs loaded."""
    register_apis('patent', APIS)
    bot.memory['patent_loaded'] = True
    bot.memory['patent_count'] = 2


def shutdown(bot):
    """Module shutdown."""
    bot.memory['patent_loaded'] = False


@plugin.command('patent_patentsview')
@plugin.example('`patent_patentsview python')
@plugin.example('`patent_patentsview "machine learning"')
def patent_patentsview(bot, trigger):
    """Search US patents using PatentsView API."""
    # PatentsView: https://patentsview.org/apis/purpose
    # Endpoint: POST https://api.patentsview.org/patents/query
    # Uses POST with JSON query format

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `patent_patentsview <search_term>')
        bot.notice(trigger.nick, 'Example: `patent_patentsview python')
        bot.notice(trigger.nick, 'Example: `patent_patentsview "machine learning"')
        return

    search_term = trigger.group(2).strip()

    logger.info(f'PatentsView search: {search_term}')

    # Build PatentsView query JSON
    query_data = {
        "q": {
            "_text_any": {
                "patent_abstract": search_term
            }
        },
        "f": [
            "patent_number",
            "patent_title",
            "patent_date",
            "inventor_first_name",
            "inventor_last_name"
        ],
        "o": {
            "per_page": 3
        }
    }

    url = 'https://api.patentsview.org/patents/query'

    logger.debug(f'Searching PatentsView: {url}')
    data = http.post(url, data=json.dumps(query_data).encode('utf-8'),
                     headers={'Content-Type': 'application/json'})

    if not data:
        bot.notice(trigger.nick, 'Failed to search PatentsView. The API may be temporarily unavailable.')
        return

    if isinstance(data, dict) and data.get('error'):
        error_reason = data.get('reason', 'Unknown error')
        if 'discontinued' in error_reason.lower():
            bot.notice(trigger.nick, 'PatentsView API appears to be discontinued or changed.')
            bot.notice(trigger.nick, 'Visit https://patentsview.org/ for the latest API information.')
        else:
            bot.notice(trigger.nick, f'PatentsView API error: {error_reason}')
        return

    patents = data.get('patents', [])

    if not patents:
        bot.notice(trigger.nick, f'No patents found for "{search_term}".')
        return

    total_found = data.get('total_patent_count', len(patents))
    bot.say(f'PatentsView - Found {total_found:,} patent(s) for "{search_term}" (showing {len(patents)}):')

    for patent in patents:
        patent_num = patent.get('patent_number', 'Unknown')
        title = patent.get('patent_title', 'Unknown')
        date = patent.get('patent_date', 'Unknown')
        inventors = patent.get('inventors', [])

        response = f"{formatter.bold(title)}"
        response += f" | {formatter.monospace(f'US{patent_num}')}"
        if date:
            date_short = date[:10] if len(date) >= 10 else date
            response += f" | {formatter.monospace(date_short)}"
        bot.say(formatter.truncate(response, max_len=400))

        if inventors:
            inventor_list = []
            for inv in inventors[:2]:  # Show first 2 inventors
                first = inv.get('inventor_first_name', '')
                last = inv.get('inventor_last_name', '')
                if first and last:
                    inventor_list.append(f"{first} {last}")
            if inventor_list:
                bot.say(f"  Inventors: {formatter.italic(', '.join(inventor_list))}")


@plugin.command('patent_uspto')
@plugin.example('`patent_uspto 10000000')
@plugin.example('`patent_uspto US10000000')
def patent_uspto(bot, trigger):
    """Get US patent information using USPTO APIs."""
    # USPTO: https://www.uspto.gov/learning-and-resources/open-data-and-mobility
    # Patent Public Search: https://ppubs.uspto.gov/
    # Note: USPTO doesn't have a simple REST API for direct patent lookup
    # We'll provide helpful information and links

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `patent_uspto <patent_number>')
        bot.notice(trigger.nick, 'Example: `patent_uspto 10000000')
        bot.notice(trigger.nick, 'Example: `patent_uspto US10000000')
        bot.notice(trigger.nick, 'Note: USPTO requires web interface for full patent details.')
        return

    patent_num = trigger.group(2).strip()

    # Clean patent number (remove US prefix if present)
    if patent_num.upper().startswith('US'):
        patent_num = patent_num[2:]

    if not patent_num.isdigit() or len(patent_num) < 7:
        bot.notice(trigger.nick, 'Patent number must be numeric (e.g., 10000000)')
        return

    logger.info(f'USPTO patent lookup: {patent_num}')

    # Format patent number with leading zeros if needed
    patent_formatted = patent_num.zfill(8)

    bot.say(f"{formatter.bold('USPTO Patent')}: {formatter.monospace(f'US{patent_formatted}')}")
    bot.say(f"Search URL: {formatter.monospace('https://ppubs.uspto.gov/pubwebapp/static/pages/ppubsbasic.html')}")
    bot.notice(trigger.nick, 'USPTO Patent Public Search:')
    bot.notice(trigger.nick, 'Visit https://ppubs.uspto.gov/pubwebapp/static/pages/ppubsbasic.html')
    bot.notice(trigger.nick, f'Search for patent number: US{patent_formatted}')
    bot.notice(trigger.nick, 'USPTO bulk data: https://bulkdata.uspto.gov/')
