"""
Sopel module for Business APIs.
Supports 7 public APIs with no authentication required.
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
        'name': 'Domainsdb.info',
        'description': 'Registered Domain Names Search',
        'link': 'https://domainsdb.info/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'markerapi',
        'description': 'Trademark Search',
        'link': 'https://markerapi.com',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Tenders in Hungary',
        'description': 'Get data for procurements in Hungary in JSON format',
        'link': 'https://tenders.guru/hu/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Tenders in Poland',
        'description': 'Get data for procurements in Poland in JSON format',
        'link': 'https://tenders.guru/pl/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Tenders in Romania',
        'description': 'Get data for procurements in Romania in JSON format',
        'link': 'https://tenders.guru/ro/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Tenders in Spain',
        'description': 'Get data for procurements in Spain in JSON format',
        'link': 'https://tenders.guru/es/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Tenders in Ukraine',
        'description': 'Get data for procurements in Ukraine in JSON format',
        'link': 'https://tenders.guru/ua/api',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('business')
@plugin.command('business')
@plugin.example(f'.business')
def business_list(bot, trigger):
    """List all available Business APIs."""
    bot.say(f'Available Business APIs (7):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .business_info <name> for details')


@plugin.command('business_info')
@plugin.example(f'.business_info <name>')
def business_info(bot, trigger):
    """Get information about a specific Business API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .business_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('business_search')
@plugin.example(f'.business_search <query>')
def business_search(bot, trigger):
    """Search Business APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .business_search <query>')
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


@plugin.command('domain_domainsdb')
@plugin.example('.domain_domainsdb example')
@plugin.example('.domain_domainsdb github')
def domain_domainsdb(bot, trigger):
    """Search for registered domains using DomainsDB API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .domain_domainsdb <domain_name>')
        return
    
    domain = trigger.group(2).strip()
    logger.info(f'Domain search: {domain}')
    
    encoded_domain = http.quote(domain)
    url = f'https://api.domainsdb.info/v1/domains/search?domain={encoded_domain}&limit=3'
    
    logger.debug(f'Searching domains: {url}')
    data = http.get(url)
    
    if not data or 'domains' not in data:
        bot.notice(trigger.nick, f'No domains found for "{domain}" or API error.')
        return
    
    domains = data.get('domains', [])[:3]
    
    if not domains:
        bot.notice(trigger.nick, f'No domains found for "{domain}"')
        return
    
    bot.say(f'Found {len(domains)} domain(s) for "{domain}":')
    for domain_info in domains:
        domain_name = domain_info.get('domain', 'Unknown')
        create_date = domain_info.get('create_date', 'Unknown')
        update_date = domain_info.get('update_date', 'Unknown')
        country = domain_info.get('country', 'Unknown')
        
        response = f"{formatter.bold(domain_name)}"
        if country != 'Unknown':
            response += f" | Country: {formatter.italic(country)}"
        if create_date != 'Unknown':
            create_short = create_date[:10] if len(create_date) >= 10 else create_date
            response += f" | Created: {formatter.monospace(create_short)}"
        
        bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Business APIs loaded."""
    bot.memory['business_loaded'] = True
    bot.memory['business_count'] = 7
    logger.info('Business module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['business_loaded'] = False
    logger.info('Business module unloaded')
