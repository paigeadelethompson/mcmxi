"""
Sopel module for Open Data APIs.
Supports 19 public APIs with no authentication required.
"""

import os
import sys

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, get_command_prefix, IRCFormatter, get_module_logger, register_apis

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)
formatter = IRCFormatter()


# API definitions
APIS = [
    {
        'name': '18F',
        'description': 'Unofficial US Federal Government API Development',
        'link': 'http://18f.github.io/API-All-the-X/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Archive.org',
        'description': 'The Internet Archive',
        'link': 'https://archive.readme.io/docs',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'ArgentinaDatos',
        'description': 'Unofficial Argentinian data API',
        'link': 'https://argentinadatos.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'BotsArchive',
        'description': 'JSON formatted details about Telegram Bots available in database',
        'link': 'https://botsarchive.com/docs.html',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Callook.info',
        'description': 'United States ham radio callsigns',
        'link': 'https://callook.info',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'CollegeScoreCard.ed.gov',
        'description': 'Data on higher education institutions in the United States',
        'link': 'https://collegescorecard.ed.gov/data/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'French Address Search',
        'description': 'Address search via the French Government',
        'link': 'https://geo.api.gouv.fr/adresse',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Lowy Asia Power Index',
        'description': 'Get measure resources and influence to rank the relative power of states in Asia',
        'link': 'https://github.com/0x0is1/lowy-index-api-docs',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Microlink.io',
        'description': 'Extract structured data from any website',
        'link': 'https://microlink.io',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Nobel Prize',
        'description': 'Open data about nobel prizes and events',
        'link': 'https://www.nobelprize.org/about/developer-zone-2/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Open Data Minneapolis',
        'description': 'Spatial (GIS) and non-spatial city data for Minneapolis',
        'link': 'https://opendata.minneapolismn.gov/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'openAFRICA',
        'description': 'Large datasets repository of African open data',
        'link': 'https://africaopendata.org/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'OpenSanctions',
        'description': 'Data on international sanctions, crime and politically exposed persons',
        'link': 'https://www.opensanctions.org/docs/api/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Sofiaplan',
        'description': 'Access to urban research data for the Bulgarian capital Sofia',
        'link': 'https://sofiaplan.bg/api/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Umeå Open Data',
        'description': 'Open data of the city Umeå in northern Sweden',
        'link': 'https://opendata.umea.se/api/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Universities List',
        'description': 'University names, countries and domains',
        'link': 'https://github.com/Hipo/university-domains-list',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'University of Oslo',
        'description': 'Courses, lecture videos, detailed information for courses etc. for the University of Oslo (Norway)',
        'link': 'https://data.uio.no/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Urban Observatory',
        'description': 'The largest set of publicly available real time urban data in the UK',
        'link': 'https://urbanobservatory.ac.uk',
        'https': False,
        'cors': 'no',
    },
    {
        'name': 'Wikipedia',
        'description': 'Mediawiki Encyclopedia',
        'link': 'https://www.mediawiki.org/wiki/API:Main_page',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('open_data')
@plugin.command('opendata')
@plugin.example('`open_data')
def open_data_list(bot, trigger):
    """List all available Open Data APIs."""
    bot.say('Available Open Data APIs (19):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use {prefix}open_data_info <name> for details')


@plugin.command('open_data_info')
@plugin.example('`open_data_info <name>')
def open_data_info(bot, trigger):
    """Get information about a specific Open Data API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `open_data_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('open_data_search')
@plugin.example('`open_data_search <query>')
def open_data_search(bot, trigger):
    """Search Open Data APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `open_data_search <query>')
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


@plugin.command('university_universitieslist')
@plugin.example('`university_universitieslist mit')
@plugin.example('`university_universitieslist usa')
def university_universitieslist(bot, trigger):
    """Search for universities using Universities List API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `university_universitieslist <name/country>')
        bot.notice(trigger.nick, 'Example: `university_universitieslist mit')
        return

    query = trigger.group(2).strip()
    logger.info(f'University search: {query}')

    http.quote(query)
    url = 'https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json'

    logger.debug(f'Fetching universities list: {url}')
    data = http.get(url)

    if not data or not isinstance(data, list):
        bot.notice(trigger.nick, 'Failed to fetch universities data. Please try again.')
        return

    # Search for matching universities
    query_lower = query.lower()
    matches = []
    for uni in data:
        name = uni.get('name', '')
        country = uni.get('country', '')
        domains = uni.get('domains', [])

        if (query_lower in name.lower() or query_lower in country.lower() or
            any(query_lower in d.lower() for d in domains)):
            matches.append(uni)
            if len(matches) >= 3:
                break

    if not matches:
        bot.notice(trigger.nick, f'No universities found for "{query}"')
        return

    bot.say(f'Found {len(matches)} university(ies) for "{query}":')
    for uni in matches:
        name = uni.get('name', 'Unknown')
        country = uni.get('country', 'Unknown')
        domains = uni.get('domains', [])

        response = f"{formatter.bold(name)}"
        if country:
            response += f" {formatter.italic(f'({country})')}"
        if domains:
            response += f" | Domain: {formatter.monospace(domains[0])}"

        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('hamradio_callook')
@plugin.example('`hamradio_callook K1ABC')
@plugin.example('`hamradio_callook W1AW')
def hamradio_callook(bot, trigger):
    """Look up US ham radio callsign information using Callook.info API."""
    # Callook.info: https://callook.info
    # Endpoint: GET https://callook.info/{callsign}/json

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `hamradio_callook <callsign>')
        bot.notice(trigger.nick, 'Example: `hamradio_callook K1ABC')
        return

    callsign = trigger.group(2).strip().upper()

    logger.info(f'Callook lookup: {callsign}')

    url = f'https://callook.info/{http.quote(callsign)}/json'

    logger.debug(f'Fetching callsign info: {url}')
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to fetch callsign information.')
        return

    if data.get('status') != 'VALID':
        error_msg = data.get('message', 'Invalid callsign')
        bot.notice(trigger.nick, f'Invalid callsign: {error_msg}')
        return

    current = data.get('current', {})
    name = data.get('name', 'Unknown')
    address = data.get('address', {})
    location = data.get('location', {})
    other_info = data.get('otherInfo', {})

    response = f"{formatter.bold(callsign)}"
    if name:
        response += f" | {formatter.italic(name)}"
    if current.get('operClass'):
        response += f" | Class: {formatter.monospace(current['operClass'])}"

    bot.say(formatter.truncate(response, max_len=400))

    if address.get('line2'):
        bot.say(f"Location: {formatter.italic(address['line2'])}")
    if location.get('gridsquare'):
        bot.say(f"Grid Square: {formatter.monospace(location['gridsquare'])}")
    if other_info.get('grantDate'):
        bot.say(f"Granted: {formatter.monospace(other_info['grantDate'])} | Expires: {formatter.monospace(other_info.get('expiryDate', 'N/A'))}")


@plugin.command('metadata_microlink')
@plugin.example('`metadata_microlink https://example.com')
@plugin.example('`metadata_microlink https://github.com')
def metadata_microlink(bot, trigger):
    """Extract structured metadata from a website using Microlink.io API."""
    # Microlink.io: https://microlink.io
    # Endpoint: GET https://api.microlink.io?url={url}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `metadata_microlink <url>')
        bot.notice(trigger.nick, 'Example: `metadata_microlink https://example.com')
        return

    url_input = trigger.group(2).strip()

    # Add https:// if no scheme provided
    if not url_input.startswith(('http://', 'https://')):
        url_input = 'https://' + url_input

    logger.info(f'Microlink metadata extraction: {url_input}')

    encoded_url = http.quote(url_input)
    url = f'https://api.microlink.io?url={encoded_url}'

    logger.debug(f'Extracting metadata: {url}')
    data = http.get(url)

    if not data or data.get('status') != 'success':
        bot.notice(trigger.nick, 'Failed to extract metadata from URL.')
        return

    metadata = data.get('data', {})
    title = metadata.get('title', 'Unknown')
    description = metadata.get('description', '')
    author = metadata.get('author', '')
    publisher = metadata.get('publisher', '')
    date = metadata.get('date', '')

    response = f"{formatter.bold(title)}"
    if publisher:
        response += f" | {formatter.italic(publisher)}"
    if author:
        response += f" | Author: {formatter.italic(author)}"
    bot.say(formatter.truncate(response, max_len=400))

    if description:
        desc_short = description[:150] + '...' if len(description) > 150 else description
        bot.say(f"  {formatter.italic(desc_short)}")
    if date:
        date_short = date[:10] if len(date) >= 10 else date
        bot.say(f"Date: {formatter.monospace(date_short)}")


@plugin.command('nobel_prize')
@plugin.example('`nobel_prize einstein')
@plugin.example('`nobel_prize physics')
def nobel_prize(bot, trigger):
    """Search Nobel Prize laureates using Nobel Prize API."""
    # Nobel Prize: https://www.nobelprize.org/about/developer-zone-2/
    # Endpoint: GET https://www.nobelprize.org/api/laureate

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `nobel_prize <search_term>')
        bot.notice(trigger.nick, 'Examples: .nobel_prize einstein')
        bot.notice(trigger.nick, '          .nobel_prize physics')
        return

    search_term = trigger.group(2).strip()

    logger.info(f'Nobel Prize search: {search_term}')

    url = 'https://www.nobelprize.org/api/laureate'

    logger.debug(f'Fetching Nobel Prize data: {url}')
    data = http.get(url)

    if not data or 'laureates' not in data:
        bot.notice(trigger.nick, 'Failed to fetch Nobel Prize data.')
        return

    laureates = data.get('laureates', [])

    # Filter laureates by search term
    if search_term:
        search_lower = search_term.lower()
        laureates = [l for l in laureates if
                     search_lower in l.get('firstname', '').lower() or
                     search_lower in l.get('surname', '').lower() or
                     any(search_lower in p.get('category', {}).get('en', '').lower()
                         for p in l.get('nobelPrizes', []))]

    if not laureates:
        bot.notice(trigger.nick, f'No Nobel Prize laureates found for "{search_term}".')
        return

    bot.say(f'Nobel Prize Laureates (showing {min(3, len(laureates))}):')
    for laureate in laureates[:3]:
        firstname = laureate.get('firstname', '')
        surname = laureate.get('surname', '')
        prizes = laureate.get('nobelPrizes', [])

        response = f"{formatter.bold(f'{firstname} {surname}')}"
        if prizes:
            prize = prizes[0]
            category = prize.get('category', {}).get('en', 'Unknown')
            year = prize.get('awardYear', 'Unknown')
            motivation = prize.get('motivation', {}).get('en', '')

            response += f" | {formatter.italic(category)} ({year})"
            bot.say(formatter.truncate(response, max_len=400))
            if motivation:
                mot_short = motivation[:120] + '...' if len(motivation) > 120 else motivation
                bot.say(f"  {formatter.italic(mot_short)}")
        else:
            bot.say(formatter.truncate(response, max_len=400))


@plugin.command('archive_search')
@plugin.example('`archive_search computer')
@plugin.example('`archive_search "the beatles"')
def archive_search(bot, trigger):
    """Search Internet Archive using Archive.org API."""
    # Archive.org: https://archive.readme.io/docs
    # Endpoint: GET https://archive.org/advancedsearch.php?q={query}&output=json&rows={limit}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `archive_search <search_term>')
        bot.notice(trigger.nick, 'Example: `archive_search computer')
        bot.notice(trigger.nick, 'Example: `archive_search "the beatles"')
        return

    search_term = trigger.group(2).strip()

    logger.info(f'Internet Archive search: {search_term}')

    encoded_query = http.quote(search_term)
    url = f'https://archive.org/advancedsearch.php?q={encoded_query}&output=json&rows=3&fl=identifier,title,creator,date,downloads'

    logger.debug(f'Searching Archive.org: {url}')
    data = http.get(url)

    if not data or 'response' not in data:
        bot.notice(trigger.nick, 'Failed to search Internet Archive.')
        return

    docs = data.get('response', {}).get('docs', [])

    if not docs:
        bot.notice(trigger.nick, f'No items found for "{search_term}"')
        return

    total_found = data.get('response', {}).get('numFound', len(docs))
    bot.say(f'Internet Archive - Found {total_found:,} item(s) for "{search_term}" (showing {len(docs)}):')

    for doc in docs:
        identifier = doc.get('identifier', 'Unknown')
        title = doc.get('title', 'Unknown')
        creator = doc.get('creator', [])
        date = doc.get('date', '')
        downloads = doc.get('downloads', 0)

        response = f"{formatter.bold(title)}"
        if creator:
            creator_str = creator[0] if isinstance(creator, list) else creator
            response += f" | {formatter.italic(creator_str)}"
        if date:
            date_short = date[:10] if len(date) >= 10 else date
            response += f" | {formatter.monospace(date_short)}"
        bot.say(formatter.truncate(response, max_len=400))

        if downloads:
            bot.say(f"  Downloads: {formatter.monospace(f'{downloads:,}')} | ID: {formatter.monospace(identifier)}")


def setup(bot):
    """Module setup - Open Data APIs loaded."""
    register_apis('open_data', APIS)
    bot.memory['open_data_loaded'] = True
    bot.memory['open_data_count'] = 19
    logger.info('Open Data module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['open_data_loaded'] = False
    logger.info('Open Data module unloaded')
