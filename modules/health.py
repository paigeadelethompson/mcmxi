"""
Sopel module for Health APIs.
Supports 20 public APIs with no authentication required.
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
        'name': 'Coronavirus in the UK',
        'description': 'UK Government coronavirus data, including deaths and cases by region',
        'link': 'https://coronavirus.data.gov.uk/details/developers-guide',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Covid Tracking Project',
        'description': 'Covid-19 data for the US',
        'link': 'https://covidtracking.com/data/api/version-2',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Covid-19',
        'description': 'Covid 19 cases, deaths and recovery per country',
        'link': 'https://github.com/M-Media-Group/Covid-19-API',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Covid-19 Datenhub',
        'description': 'Maps, datasets, applications and more in the context of COVID-19',
        'link': 'https://npgeo-corona-npgeo-de.hub.arcgis.com',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Covid-19 Government Response',
        'description': 'Government measures tracker to fight against the Covid-19 pandemic',
        'link': 'https://covidtracker.bsg.ox.ac.uk',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Covid-19 India',
        'description': 'Covid 19 statistics state and district wise about cases, vaccinations, recovery within India',
        'link': 'https://data.covid19india.org/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Covid-19 JHU CSSE',
        'description': 'Open-source API for exploring Covid19 cases based on JHU CSSE',
        'link': 'https://nuttaphat.com/covid19-api/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Covid-19 Live Data',
        'description': 'Global and countrywise data of Covid 19 daily Summary, confirmed cases, recovered and deaths',
        'link': 'https://github.com/mathdroid/covid-19-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Covid-19 Philippines',
        'description': 'Unofficial Covid-19 Web API for Philippines from data collected by DOH',
        'link': 'https://github.com/Simperfy/Covid-19-API-Philippines-DOH',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'COVID-19 Tracker Canada',
        'description': 'Details on Covid-19 cases across Canada',
        'link': 'https://api.covid19tracker.ca/docs/1.0/overview',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'COVID-19 Tracker Sri Lanka',
        'description': 'Provides situation of the COVID-19 patients reported in Sri Lanka',
        'link': 'https://www.hpb.health.gov.lk/en/api-documentation',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Dataflow Kit COVID-19',
        'description': 'COVID-19 live statistics into sites per hour',
        'link': 'https://covid-19.dataflowkit.com',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Healthcare.gov',
        'description': 'Educational content about the US Health Insurance Marketplace',
        'link': 'https://www.healthcare.gov/developers/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Humanitarian Data Exchange',
        'description': 'Humanitarian Data Exchange (HDX) is open platform for sharing data across crises and organisations',
        'link': 'https://data.humdata.org/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'LAPIS',
        'description': 'SARS-CoV-2 genomic sequences from public sources',
        'link': 'https://cov-spectrum.ethz.ch/public',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Makeup',
        'description': 'Makeup Information',
        'link': 'http://makeup-api.herokuapp.com/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'MyVaccination',
        'description': 'Vaccination data for Malaysia',
        'link': 'https://documenter.getpostman.com/view/16605343/Tzm8GG7u',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'NPPES',
        'description': 'National Plan & Provider Enumeration System, info on healthcare providers registered in US',
        'link': 'https://npiregistry.cms.hhs.gov/registry/help-api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Data NHS Scotland',
        'description': 'Medical reference data and statistics by Public Health Scotland',
        'link': 'https://www.opendata.nhs.scot',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Disease',
        'description': 'API for Current cases and more stuff about COVID-19 and Influenza',
        'link': 'https://disease.sh/',
        'https': True,
        'cors': 'yes',
    },
]


@plugin.command('health')
@plugin.command('health')
@plugin.example(f'.health')
def health_list(bot, trigger):
    """List all available Health APIs."""
    bot.say(f'Available Health APIs (20):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .health_info <name> for details')


@plugin.command('health_info')
@plugin.example(f'.health_info <name>')
def health_info(bot, trigger):
    """Get information about a specific Health API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .health_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('health_search')
@plugin.example(f'.health_search <query>')
def health_search(bot, trigger):
    """Search Health APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .health_search <query>')
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


@plugin.command('covid_opendisease')
@plugin.example('.covid_opendisease')
@plugin.example('.covid_opendisease USA')
def covid_opendisease(bot, trigger):
    """Get COVID-19 data using Open Disease API."""
    country = trigger.group(2).strip() if trigger.group(2) else 'all'
    
    logger.info(f'COVID-19 data lookup: {country}')
    
    if country.lower() == 'all':
        url = 'https://disease.sh/v3/covid-19/all'
    else:
        encoded_country = http.quote(country)
        url = f'https://disease.sh/v3/covid-19/countries/{encoded_country}'
    
    logger.debug(f'Fetching COVID-19 data: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, f'Failed to fetch COVID-19 data for "{country}" or API error.')
        return
    
    country_name = data.get('country', 'World')
    cases = data.get('cases', 0)
    deaths = data.get('deaths', 0)
    recovered = data.get('recovered', 0)
    active = data.get('active', 0)
    today_cases = data.get('todayCases', 0)
    today_deaths = data.get('todayDeaths', 0)
    
    response = f"{formatter.bold(country_name)} COVID-19:"
    response += f" Cases: {formatter.bold(f'{cases:,}')} | Deaths: {formatter.bold(f'{deaths:,}')} | Recovered: {formatter.bold(f'{recovered:,}')}"
    if active:
        response += f" | Active: {formatter.monospace(f'{active:,}')}"
    if today_cases or today_deaths:
        response += f" | Today: {formatter.italic(f'+{today_cases:,} cases, +{today_deaths:,} deaths')}"
    
    bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Health APIs loaded."""
    bot.memory['health_loaded'] = True
    bot.memory['health_count'] = 20
    logger.info('Health module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['health_loaded'] = False
    logger.info('Health module unloaded')
