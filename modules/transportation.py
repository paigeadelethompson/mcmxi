"""
Sopel module for Transportation APIs.
Supports 30 public APIs with no authentication required.
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
        'name': 'adsbdb',
        'description': 'Open access to aircraft, airline, and flight route data',
        'link': 'https://www.adsbdb.com',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'airportsapi',
        'description': 'Get name and website-URL for airports by ICAO code',
        'link': 'https://airport-web.appspot.com/api/docs/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'AviationAPI',
        'description': 'FAA Aeronautical Charts and Publications, Airport Information, and Airport Weather',
        'link': 'https://docs.aviationapi.com',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'BC Ferries',
        'description': 'Sailing times and capacities for BC Ferries',
        'link': 'https://www.bcferriesapi.ca',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Community Transit',
        'description': 'Transitland API',
        'link': 'https://github.com/transitland/transitland-datastore/blob/master/README.md#api-endpoints',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'facha',
        'description': 'Aircraft Tracking, AIS Ship Tracking, Temporary Email Detection, IP GeoLocation, Package Tracking',
        'link': 'https://docs.api.facha.dev/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Fuel Prices at Spanish Gas Stations',
        'description': 'Provides information about fuel prices at gas stations in Spain',
        'link': 'https://datos.gob.es/en/apidata',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Icelandic APIs',
        'description': 'Open APIs that deliver services in or regarding Iceland',
        'link': 'http://docs.apis.is/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Konkan Railway Live Train Position',
        'description': "Realtime data for trains on India\'s Konkan Railway",
        'link': 'https://konkan-railway-api.vercel.app/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Metro Lisboa',
        'description': 'Delays in subway lines',
        'link': 'http://app.metrolisboa.pt/status/getLinhas.php',
        'https': False,
        'cors': 'no',
    },
    {
        'name': 'REFUGE Restrooms',
        'description': 'Provides safe restroom access for transgender, intersex and gender nonconforming individuals',
        'link': 'https://www.refugerestrooms.org/api/docs/#!/restrooms',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'TransitLand',
        'description': 'Transit Aggregation',
        'link': 'https://www.transit.land/documentation/datastore/api-endpoints.html',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Atlanta, US',
        'description': 'Marta',
        'link': 'http://www.itsmarta.com/app-developer-resources.aspx',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Auckland, New Zealand',
        'description': 'Auckland Transport',
        'link': 'https://dev-portal.at.govt.nz/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Belgium',
        'description': 'The iRail API is a third-party API for Belgian public transport by train',
        'link': 'https://docs.irail.be/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Transport for Berlin, Germany',
        'description': 'Third-party VBB API',
        'link': 'https://github.com/derhuerst/vbb-rest/blob/5/docs/api.md',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Budapest, Hungary',
        'description': 'Budapest public transport API',
        'link': 'https://bkkfutar.docs.apiary.io',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Czech Republic',
        'description': 'Czech transport API',
        'link': 'https://www.chaps.cz/eng/products/idos-internet',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Grenoble, France',
        'description': 'Grenoble public transport',
        'link': 'https://www.mobilites-m.fr/pages/opendata/OpenDataApi.html',
        'https': False,
        'cors': 'no',
    },
    {
        'name': 'Transport for Hessen, Germany',
        'description': 'RMV API (Public Transport in Hessen)',
        'link': 'https://opendata.rmv.de/site/start.html',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Los Angeles, US',
        'description': 'Data about positions of Metro vehicles in real time and travel their routes',
        'link': 'https://developer.metro.net/api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Norway',
        'description': 'Transport APIs and dataset for Norway',
        'link': 'https://developer.entur.org/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Paris, France',
        'description': 'RATP Open Data API',
        'link': 'http://data.ratp.fr/api/v1/console/datasets/1.0/search/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Spain',
        'description': 'Public trains of Spain',
        'link': 'https://data.renfe.com/api/1/util/snippet/api_info.html?resource_id=a2368cff-1562-4dde-8466-9635ea3a572a',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Switzerland',
        'description': 'Swiss public transport API',
        'link': 'https://transport.opendata.ch/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for The Netherlands',
        'description': 'OVAPI, country-wide public transport',
        'link': 'https://github.com/skywave/KV78Turbo-OVAPI/wiki',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for Toronto, Canada',
        'description': 'TTC',
        'link': 'https://myttc.ca/developers',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Transport for United States',
        'description': 'NextBus API',
        'link': 'https://retro.umoiq.com/xmlFeedDocs/NextBusXMLFeed.pdf',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'transport.rest',
        'description': 'Community maintained, developer-friendly public transport API',
        'link': 'https://transport.rest',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Velib metropolis, Paris, France',
        'description': 'Velib Open Data API',
        'link': 'https://www.velib-metropole.fr/donnees-open-data-gbfs-du-service-velib-metropole',
        'https': True,
        'cors': 'no',
    },
]


@plugin.command('transportation')
@plugin.command('transportation')
@plugin.example(f'.transportation')
def transportation_list(bot, trigger):
    """List all available Transportation APIs."""
    bot.say(f'Available Transportation APIs (30):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .transportation_info <name> for details')


@plugin.command('transportation_info')
@plugin.example(f'.transportation_info <name>')
def transportation_info(bot, trigger):
    """Get information about a specific Transportation API."""
    if not trigger.group(2):
        bot.say(f'Usage: .transportation_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('transportation_search')
@plugin.example(f'.transportation_search <query>')
def transportation_search(bot, trigger):
    """Search Transportation APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .transportation_search <query>')
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
    """Module setup - Transportation APIs loaded."""
    bot.memory['transportation_loaded'] = True
    bot.memory['transportation_count'] = 30


def shutdown(bot):
    """Module shutdown."""
    bot.memory['transportation_loaded'] = False


@plugin.command('airport_airportsapi')
@plugin.example('.airport_airportsapi KJFK')
def airport_airportsapi(bot, trigger):
    """Get airport information by ICAO code using airportsapi."""
    # airportsapi: https://airport-web.appspot.com/api/docs/
    # Endpoint: GET https://airport-web.appspot.com/api/airport/{icao}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .airport_airportsapi <ICAO_code>')
        bot.notice(trigger.nick, 'Example: .airport_airportsapi KJFK')
        return
    
    icao = trigger.group(2).strip().upper()
    
    # Validate ICAO code (4 characters, alphanumeric)
    if not icao.isalnum() or len(icao) != 4:
        bot.notice(trigger.nick, 'ICAO code must be 4 alphanumeric characters.')
        return
    
    logger.info(f'Airport lookup: {icao}')
    
    url = f'https://airport-web.appspot.com/api/airport/{http.quote(icao)}'
    
    logger.debug(f'Looking up airport: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, f'Airport "{icao}" not found or API error.')
        return
    
    icao_code = data.get('icao', icao)
    name = data.get('name', 'Unknown')
    city = data.get('city', 'Unknown')
    country = data.get('country', 'Unknown')
    website = data.get('website', '')
    
    response = f"{formatter.bold(name)} {formatter.monospace(f'({icao_code})')}"
    if city and city != 'Unknown':
        response += f" | {formatter.italic(city)}"
    if country and country != 'Unknown':
        response += f", {formatter.italic(country)}"
    if website:
        response += f" | {formatter.monospace(website)}"
    
    bot.say(formatter.truncate(response, max_len=400))
