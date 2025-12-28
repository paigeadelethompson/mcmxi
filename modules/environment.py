"""
Sopel module for Environment APIs.
Supports 8 public APIs with no authentication required.
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
        'name': 'Air Quality Index',
        'description': 'Real-time air quality data including AQI and pollutant concentrations for worldwide locations',
        'link': 'https://www.juheapi.com/api-catalog/aqi',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Danish data service Energi',
        'description': 'Open energy data from Energinet to society',
        'link': 'https://www.energidataservice.dk/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'GrünstromIndex',
        'description': 'Green Power Index for Germany (Grünstromindex/GSI)',
        'link': 'https://gruenstromindex.de/',
        'https': False,
        'cors': 'yes',
    },
    {
        'name': 'Luchtmeetnet',
        'description': 'Predicted and actual air quality components for The Netherlands (RIVM)',
        'link': 'https://api-docs.luchtmeetnet.nl/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'National Grid ESO',
        'description': 'Open data from Great Britain’s Electricity System Operator',
        'link': 'https://data.nationalgrideso.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'PM2.5 Open Data Portal',
        'description': 'Open low-cost PM2.5 sensor data',
        'link': 'https://pm25.lass-net.org/#apis',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'UK Carbon Intensity',
        'description': 'The Official Carbon Intensity API for Great Britain developed by National Grid',
        'link': 'https://carbon-intensity.github.io/api-definitions/#carbon-intensity-api-v1-0-0',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Website Carbon',
        'description': 'API to estimate the carbon footprint of loading web pages',
        'link': 'https://api.websitecarbon.com/',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('environment')
@plugin.command('environment')
@plugin.example(f'.environment')
def environment_list(bot, trigger):
    """List all available Environment APIs."""
    bot.say(f'Available Environment APIs (8):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .environment_info <name> for details')


@plugin.command('environment_info')
@plugin.example(f'.environment_info <name>')
def environment_info(bot, trigger):
    """Get information about a specific Environment API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .environment_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('environment_search')
@plugin.example(f'.environment_search <query>')
def environment_search(bot, trigger):
    """Search Environment APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .environment_search <query>')
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


@plugin.command('carbon_ukcarbonintensity')
@plugin.example('.carbon_ukcarbonintensity')
def carbon_ukcarbonintensity(bot, trigger):
    """Get UK carbon intensity data using UK Carbon Intensity API."""
    logger.info('Fetching UK carbon intensity')
    
    # Get current carbon intensity
    url = 'https://api.carbonintensity.org.uk/intensity'
    
    logger.debug(f'Fetching carbon intensity: {url}')
    data = http.get(url)
    
    if not data or 'data' not in data or not data['data']:
        bot.notice(trigger.nick, 'Failed to fetch carbon intensity data. Please try again.')
        return
    
    current = data['data'][0]
    intensity = current.get('intensity', {})
    actual = intensity.get('actual', 'N/A')
    forecast = intensity.get('forecast', 'N/A')
    index = intensity.get('index', 'N/A')
    from_time = current.get('from', '')[:16] if current.get('from') else 'Unknown'
    to_time = current.get('to', '')[:16] if current.get('to') else 'Unknown'
    
    response = f"UK Carbon Intensity: {formatter.bold(str(actual))} {formatter.monospace('gCO₂/kWh')}"
    if forecast != 'N/A' and forecast != actual:
        response += f" {formatter.italic(f'(forecast: {forecast})')}"
    if index != 'N/A':
        response += f" | Index: {formatter.bold(index)}"
    response += f" | Period: {formatter.monospace(f'{from_time} to {to_time}')}"
    
    bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Environment APIs loaded."""
    bot.memory['environment_loaded'] = True
    bot.memory['environment_count'] = 8
    logger.info('Environment module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['environment_loaded'] = False
    logger.info('Environment module unloaded')
