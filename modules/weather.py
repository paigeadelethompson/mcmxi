"""
Sopel module for Weather APIs.
Supports 9 public APIs with no authentication required.
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
        'name': '7Timer!',
        'description': 'Weather, especially for Astroweather',
        'link': 'http://www.7timer.info/doc.php?lang=en',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'AviationWeather',
        'description': 'NOAA aviation weather forecasts and observations',
        'link': 'https://www.aviationweather.gov/dataserver',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Hong Kong Obervatory',
        'description': 'Provide weather information, earthquake information, and climate data',
        'link': 'https://www.hko.gov.hk/en/abouthko/opendata_intro.htm',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'ODWeather',
        'description': 'Weather and weather webcams',
        'link': 'http://api.oceandrivers.com/static/docs.html',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Open-Meteo',
        'description': 'Global weather forecast API for non-commercial use',
        'link': 'https://open-meteo.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'openSenseMap',
        'description': 'Data from Personal Weather Stations called senseBoxes',
        'link': 'https://api.opensensemap.org/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'RainViewer',
        'description': 'Radar data collected from different websites across the Internet',
        'link': 'https://www.rainviewer.com/api.html',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'US Weather',
        'description': 'US National Weather Service',
        'link': 'https://www.weather.gov/documentation/services-web-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'weather-api',
        'description': 'A RESTful free API to check the weather',
        'link': 'https://github.com/robertoduessmann/weather-api',
        'https': True,
        'cors': 'no',
    },
]


@plugin.command('weather')
@plugin.command('weather')
@plugin.example(f'.weather')
def weather_list(bot, trigger):
    """List all available Weather APIs."""
    bot.say(f'Available Weather APIs (9):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .weather_info <name> for details')


@plugin.command('weather_info')
@plugin.example(f'.weather_info <name>')
def weather_info(bot, trigger):
    """Get information about a specific Weather API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .weather_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('weather_search')
@plugin.example(f'.weather_search <query>')
def weather_search(bot, trigger):
    """Search Weather APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .weather_search <query>')
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


@plugin.command('weather_openmeteo')
@plugin.example('.weather_openmeteo 47.6062,-122.3321')
def weather_openmeteo(bot, trigger):
    """Get current weather using Open-Meteo API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .weather_openmeteo <lat,lon>')
        bot.notice(trigger.nick, 'Example: .weather_openmeteo 47.6062,-122.3321')
        return
    
    query = trigger.group(2).strip()
    logger.info(f'Weather query: {query}')
    
    if ',' in query:
        try:
            lat, lon = map(float, query.split(','))
            get_weather_by_coords(bot, trigger.nick, lat, lon)
        except ValueError:
            bot.notice(trigger.nick, 'Invalid coordinates. Use format: lat,lon (e.g., 47.6062,-122.3321)')
    else:
        bot.notice(trigger.nick, 'Please use coordinates: .weather_openmeteo lat,lon')


def get_weather_by_coords(bot, nick: str, lat: float, lon: float):
    """Get weather by coordinates using Open-Meteo."""
    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=auto'
    
    logger.debug(f'Fetching weather from Open-Meteo: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(nick, 'Failed to fetch weather data. Please try again later.')
        return
    
    try:
        current = data.get('current', {})
        temp = current.get('temperature_2m', 'N/A')
        humidity = current.get('relative_humidity_2m', 'N/A')
        wind_speed = current.get('wind_speed_10m', 'N/A')
        weather_code = current.get('weather_code', 0)
        
        weather_desc = get_weather_description(weather_code)
        
        response = f"Weather at {formatter.monospace(f'{lat:.2f},{lon:.2f}')}: {formatter.bold(f'{temp}°C')}"
        response += f" | Humidity: {formatter.monospace(f'{humidity}%')} | Wind: {formatter.monospace(f'{wind_speed} km/h')}"
        response += f" | {formatter.italic(weather_desc)}"
        
        bot.say(formatter.truncate(response, max_len=400))
        
    except Exception as e:
        logger.exception('Error parsing weather data', e)
        bot.notice(nick, 'Error processing weather data.')


def get_weather_description(code: int) -> str:
    """Convert WMO weather code to description."""
    codes = {
        0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
        45: 'Foggy', 48: 'Depositing rime fog',
        51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
        56: 'Light freezing drizzle', 57: 'Dense freezing drizzle',
        61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
        66: 'Light freezing rain', 67: 'Heavy freezing rain',
        71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow',
        77: 'Snow grains', 80: 'Slight rain showers', 81: 'Moderate rain showers',
        82: 'Violent rain showers', 85: 'Slight snow showers', 86: 'Heavy snow showers',
        95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail',
    }
    return codes.get(code, f'Weather code {code}')


def setup(bot):
    """Module setup - Weather APIs loaded."""
    bot.memory['weather_loaded'] = True
    bot.memory['weather_count'] = 9
    logger.info('Weather module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['weather_loaded'] = False
    logger.info('Weather module unloaded')
