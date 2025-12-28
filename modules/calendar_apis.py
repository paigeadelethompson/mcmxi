"""
Sopel module for Calendar APIs.
Supports 12 public APIs with no authentication required.
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
        'name': 'Church Calendar',
        'description': 'Catholic liturgical calendar',
        'link': 'http://calapi.inadiutorium.cz/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Czech Namedays Calendar',
        'description': 'Lookup for a name and returns nameday date',
        'link': 'https://svatky.adresa.info',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'DigiDates',
        'description': 'Various date and time calculations',
        'link': 'https://digidates.de/en/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Hebrew Calendar',
        'description': 'Convert between Gregorian and Hebrew, fetch Shabbat and Holiday times, etc',
        'link': 'https://www.hebcal.com/home/developer-apis',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'LectServe',
        'description': 'Protestant liturgical calendar',
        'link': 'http://www.lectserve.com',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Nager.Date',
        'description': 'Public holidays for more than 90 countries',
        'link': 'https://date.nager.at',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Namedays Calendar',
        'description': 'Provides namedays for multiple countries',
        'link': 'https://nameday.abalin.net',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Non-Working Days',
        'description': 'Database of ICS files for non working days',
        'link': 'https://github.com/gadael/icsdb',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Non-Working Days',
        'description': 'Simple REST API for checking working, non-working or short days for Russia, CIS, USA and other',
        'link': 'https://isdayoff.ru',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'OpenHolidays API',
        'description': 'Public and school holidays for many countries via an open REST API',
        'link': 'https://www.openholidaysapi.org/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Russian Calendar',
        'description': 'Check if a date is a Russian holiday or not',
        'link': 'https://github.com/egno/work-calendar',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'UK Bank Holidays',
        'description': 'Bank holidays in England and Wales, Scotland and Northern Ireland',
        'link': 'https://www.gov.uk/bank-holidays.json',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('calendar')
@plugin.command('calendar')
@plugin.example(f'.calendar')
def calendar_list(bot, trigger):
    """List all available Calendar APIs."""
    bot.say(f'Available Calendar APIs (12):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .calendar_info <name> for details')


@plugin.command('calendar_info')
@plugin.example(f'.calendar_info <name>')
def calendar_info(bot, trigger):
    """Get information about a specific Calendar API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .calendar_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('calendar_search')
@plugin.example(f'.calendar_search <query>')
def calendar_search(bot, trigger):
    """Search Calendar APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .calendar_search <query>')
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


@plugin.command('holiday_nager')
@plugin.example('.holiday_nager US')
@plugin.example('.holiday_nager US 2024')
def holiday_nager(bot, trigger):
    """Get public holidays using Nager.Date API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .holiday_nager <country_code> [year]')
        bot.notice(trigger.nick, 'Example: .holiday_nager US')
        bot.notice(trigger.nick, 'Example: .holiday_nager US 2024')
        return
    
    parts = trigger.group(2).strip().upper().split()
    country_code = parts[0]
    year = parts[1] if len(parts) > 1 else None
    
    if not year:
        from datetime import datetime
        year = datetime.now().year
    
    logger.info(f'Holiday lookup: {country_code} {year}')
    
    encoded_country = http.quote(country_code)
    url = f'https://date.nager.at/api/v3/PublicHolidays/{year}/{encoded_country}'
    
    logger.debug(f'Fetching holidays: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, f'No holidays found for {country_code} in {year} or API error.')
        return
    
    if not isinstance(data, list):
        bot.notice(trigger.nick, f'Invalid response format.')
        return
    
    # Get upcoming holidays (or all if none upcoming)
    from datetime import datetime
    today = datetime.now().date()
    upcoming = [h for h in data if datetime.strptime(h.get('date', ''), '%Y-%m-%d').date() >= today]
    
    if not upcoming:
        # Show last few holidays if none upcoming
        holidays = sorted(data, key=lambda x: x.get('date', ''), reverse=True)[:3]
        bot.say(f'Recent holidays for {country_code} in {year}:')
    else:
        holidays = sorted(upcoming, key=lambda x: x.get('date', ''))[:3]
        bot.say(f'Upcoming holidays for {country_code} in {year}:')
    
    for holiday in holidays:
        date = holiday.get('date', '')
        name = holiday.get('name', 'Unknown')
        local_name = holiday.get('localName', '')
        
        response = f"{formatter.bold(name)}"
        if local_name and local_name != name:
            response += f" {formatter.italic(f'({local_name})')}"
        response += f" | {formatter.monospace(date)}"
        
        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('holiday_uk')
@plugin.example('.holiday_uk')
@plugin.example('.holiday_uk england-and-wales')
def holiday_uk(bot, trigger):
    """Get UK Bank Holidays using UK Bank Holidays API."""
    # UK Bank Holidays: https://www.gov.uk/bank-holidays.json
    # Endpoint: GET https://www.gov.uk/bank-holidays.json
    # Divisions: england-and-wales, scotland, northern-ireland
    
    division = trigger.group(2).strip().lower() if trigger.group(2) else 'england-and-wales'
    
    valid_divisions = ['england-and-wales', 'scotland', 'northern-ireland']
    if division not in valid_divisions:
        bot.notice(trigger.nick, f'Invalid division. Valid: {", ".join(valid_divisions)}')
        return
    
    logger.info(f'UK Bank Holidays lookup: {division}')
    
    url = 'https://www.gov.uk/bank-holidays.json'
    
    logger.debug(f'Fetching UK bank holidays: {url}')
    data = http.get(url)
    
    if not data or division not in data:
        bot.notice(trigger.nick, 'Failed to fetch UK bank holidays.')
        return
    
    division_data = data.get(division, {})
    events = division_data.get('events', [])
    
    if not events:
        bot.notice(trigger.nick, f'No bank holidays found for {division}.')
        return
    
    # Get upcoming holidays
    from datetime import datetime
    today = datetime.now().date()
    upcoming = [e for e in events if datetime.strptime(e.get('date', ''), '%Y-%m-%d').date() >= today]
    
    if not upcoming:
        # Show last few if none upcoming
        holidays = sorted(events, key=lambda x: x.get('date', ''), reverse=True)[:3]
        division_name = division.replace('-', ' ').title()
        bot.say(f'Recent UK Bank Holidays ({division_name}):')
    else:
        holidays = sorted(upcoming, key=lambda x: x.get('date', ''))[:3]
        division_name = division.replace('-', ' ').title()
        bot.say(f'Upcoming UK Bank Holidays ({division_name}):')
    
    for holiday in holidays:
        date = holiday.get('date', '')
        title = holiday.get('title', 'Unknown')
        notes = holiday.get('notes', '')
        
        response = f"{formatter.bold(title)}"
        response += f" | {formatter.monospace(date)}"
        if notes:
            response += f" | {formatter.italic(notes)}"
        
        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('nameday_abalin')
@plugin.example('.nameday_abalin john')
@plugin.example('.nameday_abalin john us')
def nameday_abalin(bot, trigger):
    """Get nameday information using Namedays Calendar API."""
    # Namedays Calendar: https://nameday.abalin.net
    # Endpoint: GET https://nameday.abalin.net/api/V1/getdate?name={name}&country={country}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .nameday_abalin <name> [country_code]')
        bot.notice(trigger.nick, 'Example: .nameday_abalin john')
        bot.notice(trigger.nick, 'Example: .nameday_abalin john us')
        return
    
    parts = trigger.group(2).strip().split()
    name = parts[0].strip()
    country = parts[1].lower() if len(parts) > 1 else 'us'
    
    logger.info(f'Nameday lookup: {name}, country: {country}')
    
    encoded_name = http.quote(name)
    url = f'https://nameday.abalin.net/api/V1/getdate?name={encoded_name}&country={country}'
    
    logger.debug(f'Fetching nameday: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, f'Failed to fetch nameday for "{name}".')
        return
    
    # Check if it's an array or object
    if isinstance(data, list):
        if not data:
            bot.notice(trigger.nick, f'No nameday found for "{name}" in {country.upper()}.')
            return
        data = data[0]
    
    day = data.get('day', '')
    month = data.get('month', '')
    
    if not day or not month:
        bot.notice(trigger.nick, f'No nameday found for "{name}" in {country.upper()}.')
        return
    
    response = f"{formatter.bold(name)}'s nameday ({country.upper()}): {formatter.monospace(f'{month}/{day}')}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('nameday_today')
@plugin.example('.nameday_today')
@plugin.example('.nameday_today us')
def nameday_today(bot, trigger):
    """Get today's namedays using Namedays Calendar API."""
    # Namedays Calendar: https://nameday.abalin.net
    # Endpoint: GET https://nameday.abalin.net/api/V1/today?country={country}
    
    country = trigger.group(2).strip().lower() if trigger.group(2) else 'us'
    
    logger.info(f'Today\'s namedays lookup: {country}')
    
    url = f'https://nameday.abalin.net/api/V1/today?country={country}'
    
    logger.debug(f'Fetching today\'s namedays: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, f'Failed to fetch today\'s namedays for {country.upper()}.')
        return
    
    # Check if it's an array or object
    if isinstance(data, list):
        if not data:
            bot.notice(trigger.nick, f'No namedays found for today in {country.upper()}.')
            return
        data = data[0]
    
    namedays = data.get('nameday', {})
    names = []
    
    # Handle different response formats
    if isinstance(namedays, dict):
        names = namedays.get(country, [])
        if not names:
            # Try other keys
            for key in namedays.keys():
                if isinstance(namedays[key], list):
                    names = namedays[key]
                    break
    elif isinstance(namedays, list):
        names = namedays
    elif isinstance(namedays, str):
        names = [namedays]
    
    if not names:
        bot.notice(trigger.nick, f'No namedays found for today in {country.upper()}.')
        return
    
    names_str = ', '.join(names[:5])  # Show first 5 names
    response = f"Today's namedays ({country.upper()}): {formatter.bold(names_str)}"
    if len(names) > 5:
        response += f" ... and {len(names) - 5} more"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('holiday_openholidays')
@plugin.example('.holiday_openholidays US')
@plugin.example('.holiday_openholidays US 2024')
def holiday_openholidays(bot, trigger):
    """Get public holidays using OpenHolidays API."""
    # OpenHolidays API: https://www.openholidaysapi.org/
    # Endpoint: GET https://www.openholidaysapi.org/PublicHolidays?countryIsoCode={code}&languageIsoCode={lang}&validFrom={from}&validTo={to}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .holiday_openholidays <country_code> [year]')
        bot.notice(trigger.nick, 'Example: .holiday_openholidays US')
        bot.notice(trigger.nick, 'Example: .holiday_openholidays US 2024')
        return
    
    parts = trigger.group(2).strip().upper().split()
    country_code = parts[0]
    year = parts[1] if len(parts) > 1 else None
    
    if not year:
        from datetime import datetime
        year = datetime.now().year
    
    logger.info(f'OpenHolidays lookup: {country_code} {year}')
    
    valid_from = f'{year}-01-01'
    valid_to = f'{year}-12-31'
    
    url = f'https://www.openholidaysapi.org/PublicHolidays?countryIsoCode={http.quote(country_code)}&languageIsoCode=EN&validFrom={valid_from}&validTo={valid_to}'
    
    logger.debug(f'Fetching OpenHolidays: {url}')
    data = http.get(url)
    
    if not data or not isinstance(data, list):
        bot.notice(trigger.nick, f'Failed to fetch holidays for {country_code} in {year}.')
        return
    
    if not data:
        bot.notice(trigger.nick, f'No holidays found for {country_code} in {year}.')
        return
    
    # Get upcoming holidays
    from datetime import datetime
    today = datetime.now().date()
    upcoming = [h for h in data if datetime.strptime(h.get('startDate', ''), '%Y-%m-%d').date() >= today]
    
    if not upcoming:
        # Show last few if none upcoming
        holidays = sorted(data, key=lambda x: x.get('startDate', ''), reverse=True)[:3]
        bot.say(f'Recent holidays for {country_code} in {year}:')
    else:
        holidays = sorted(upcoming, key=lambda x: x.get('startDate', ''))[:3]
        bot.say(f'Upcoming holidays for {country_code} in {year}:')
    
    for holiday in holidays:
        start_date = holiday.get('startDate', '')
        name = holiday.get('name', [{}])[0].get('text', 'Unknown') if isinstance(holiday.get('name'), list) else holiday.get('name', 'Unknown')
        end_date = holiday.get('endDate', '')
        
        response = f"{formatter.bold(name)}"
        response += f" | {formatter.monospace(start_date)}"
        if end_date and end_date != start_date:
            response += f" - {formatter.monospace(end_date)}"
        
        bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Calendar APIs loaded."""
    bot.memory['calendar_loaded'] = True
    bot.memory['calendar_count'] = 12
    logger.info('Calendar module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['calendar_loaded'] = False
    logger.info('Calendar module unloaded')
