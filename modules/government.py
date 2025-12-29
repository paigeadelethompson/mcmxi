"""
Sopel module for Government APIs.
Supports 67 public APIs with no authentication required.
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
        'name': 'Api Colombia',
        'description': 'Community driven API for Colombia Public Data',
        'link': 'https://api-colombia.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Bank Negara Malaysia Open Data',
        'description': 'Malaysia Central Bank Open Data',
        'link': 'https://apikijangportal.bnm.gov.my/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'BCLaws',
        'description': 'Access to the laws of British Columbia',
        'link': 'https://www.bclaws.gov.bc.ca/civix/template/complete/api/index.html',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Brazil',
        'description': 'Community driven API for Brazil Public Data',
        'link': 'https://brasilapi.com.br/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Brazil Central Bank Open Data',
        'description': 'Brazil Central Bank Open Data',
        'link': 'https://dadosabertos.bcb.gov.br/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Brazil Receita WS',
        'description': 'Consult companies by CNPJ for Brazilian companies',
        'link': 'https://www.receitaws.com.br/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Brazilian Chamber of Deputies Open Data',
        'description': 'Provides legislative information in Apis XML and JSON, as well as files in various formats',
        'link': 'https://dadosabertos.camara.leg.br/swagger/api.html',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Census.gov',
        'description': 'The US Census Bureau provides various APIs and data sets on demographics and businesses',
        'link': 'https://www.census.gov/data/developers/data-sets.html',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'City, Berlin',
        'description': 'Berlin(DE) City Open Data',
        'link': 'https://daten.berlin.de/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'City, Gdańsk',
        'description': 'Gdańsk (PL) City Open Data',
        'link': 'https://ckan.multimediagdansk.pl/en',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'City, Gdynia',
        'description': 'Gdynia (PL) City Open Data',
        'link': 'http://otwartedane.gdynia.pl/en/api_doc.html',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'City, Helsinki',
        'description': 'Helsinki(FI) City Open Data',
        'link': 'https://hri.fi/en_gb/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'City, Lviv',
        'description': 'Lviv(UA) City Open Data',
        'link': 'https://opendata.city-adm.lviv.ua/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'City, New York Open Data',
        'description': 'New York (US) City Open Data',
        'link': 'https://opendata.cityofnewyork.us/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'City, Toronto Open Data',
        'description': 'Toronto (CA) City Open Data',
        'link': 'https://open.toronto.ca/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'civicAPI',
        'description': 'Provides live and historic election results for races across the world',
        'link': 'https://civicapi.org/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Colorado Information Marketplace',
        'description': 'Colorado State Government Open Data',
        'link': 'https://data.colorado.gov/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Data USA',
        'description': 'US Public Data',
        'link': 'https://datausa.io/about/api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Data.parliament.uk',
        'description': 'Contains live datasets including information about petitions, bills, MP votes, attendance and more',
        'link': 'https://explore.data.parliament.uk/?learnmore=Members',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Dedline.io API',
        'description': 'Data for US state voter registration deadlines and details, for primaries and general elections',
        'link': 'https://github.com/dedline-io/dedline-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'District of Columbia Open Data',
        'description': 'Contains D.C. government public datasets, including crime, GIS, financial data, and so on',
        'link': 'http://opendata.dc.gov/pages/using-apis',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'EPA',
        'description': 'Web services and data sets from the US Environmental Protection Agency',
        'link': 'https://www.epa.gov/developers/data-data-products#apis',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'FBI Wanted',
        'description': 'Access information on the FBI Wanted program',
        'link': 'https://www.fbi.gov/wanted/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Federal Register',
        'description': 'The Daily Journal of the United States Government',
        'link': 'https://www.federalregister.gov/reader-aids/developer-resources/rest-api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Interpol Red Notices',
        'description': 'Access and search Interpol Red Notices',
        'link': 'https://interpol.api.bund.dev/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Istanbul (İBB) Open Data',
        'description': 'Data sets from the İstanbul Metropolitan Municipality (İBB)',
        'link': 'https://data.ibb.gov.tr',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, ACT',
        'description': 'Australian Capital Territory Open Data',
        'link': 'https://www.data.act.gov.au/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Argentina',
        'description': 'Argentina Government Open Data',
        'link': 'https://datos.gob.ar/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Australia',
        'description': 'Australian Government Open Data',
        'link': 'https://www.data.gov.au/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Austria',
        'description': 'Austria Government Open Data',
        'link': 'https://www.data.gv.at/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Belgium',
        'description': 'Belgium Government Open Data',
        'link': 'https://data.gov.be/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Canada',
        'description': 'Canadian Government Open Data',
        'link': 'http://open.canada.ca/en',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Colombia',
        'description': 'Colombia Government Open Data',
        'link': 'https://www.dane.gov.co/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Cyprus',
        'description': 'Cyprus Government Open Data',
        'link': 'https://data.gov.cy',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Czech Republic',
        'description': 'Czech Republic Government Open Data',
        'link': 'https://data.gov.cz/english/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Denmark',
        'description': 'Denmark Government Open Data',
        'link': 'https://www.opendata.dk/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Finland',
        'description': 'Finland Government Open Data',
        'link': 'https://www.avoindata.fi/en',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Germany',
        'description': 'Germany Government Open Data',
        'link': 'https://www.govdata.de/daten/-/details/govdata-metadatenkatalog',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Ireland',
        'description': 'Ireland Government Open Data',
        'link': 'https://data.gov.ie/pages/developers',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Italy',
        'description': 'Italy Government Open Data',
        'link': 'https://www.dati.gov.it/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Kazakhstan',
        'description': 'Kazakhstan Government Open Data',
        'link': 'https://data.egov.kz/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Lithuania',
        'description': 'Lithuania Government Open Data',
        'link': 'https://data.gov.lt/public/api/1',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Malaysia',
        'description': 'Malaysia Government Open Data',
        'link': 'https://data.gov.my/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Mexico',
        'description': 'Mexican Statistical Government Open Data',
        'link': 'https://www.inegi.org.mx/datos/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Mexico',
        'description': 'Mexico Government Open Data',
        'link': 'https://datos.gob.mx/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Netherlands',
        'description': 'Netherlands Government Open Data',
        'link': 'https://data.overheid.nl/en/ondersteuning/data-publiceren/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, New Zealand',
        'description': 'New Zealand Government Open Data',
        'link': 'https://www.data.govt.nz/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Norway',
        'description': 'Norwegian Government Open Data',
        'link': 'https://data.norge.no/dataservices',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Open Government, Poland',
        'description': 'Poland Government Open Data',
        'link': 'https://dane.gov.pl/en',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Open Government, Queensland Government',
        'description': 'Queensland Government Open Data',
        'link': 'https://www.data.qld.gov.au/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Romania',
        'description': 'Romania Government Open Data',
        'link': 'http://data.gov.ro/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Saudi Arabia',
        'description': 'Saudi Arabia Government Open Data',
        'link': 'https://data.gov.sa',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Singapore',
        'description': 'Singapore Government Open Data',
        'link': 'https://data.gov.sg/developer',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Slovakia',
        'description': 'Slovakia Government Open Data',
        'link': 'https://data.gov.sk/en/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Slovenia',
        'description': 'Slovenia Government Open Data',
        'link': 'https://podatki.gov.si/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Open Government, South Australian Government',
        'description': 'South Australian Government Open Data',
        'link': 'https://data.sa.gov.au/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Spain',
        'description': 'Spain Government Open Data',
        'link': 'https://datos.gob.es/en',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Sweden',
        'description': 'Sweden Government Open Data',
        'link': 'https://www.dataportal.se/en/dataservice/91_29789/api-for-the-statistical-database',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Switzerland',
        'description': 'Switzerland Government Open Data',
        'link': 'https://handbook.opendata.swiss/de/content/nutzen/api-nutzen.html',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Taiwan',
        'description': 'Taiwan Government Open Data',
        'link': 'https://data.gov.tw/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, UK',
        'description': 'UK Government Open Data',
        'link': 'https://data.gov.uk/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, USA',
        'description': 'United States Government Open Data',
        'link': 'https://www.data.gov/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, Victoria State Government',
        'description': 'Victoria State Government Open Data',
        'link': 'https://www.data.vic.gov.au/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Government, West Australia',
        'description': 'West Australia Open Data',
        'link': 'https://data.wa.gov.au/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'PRC Exam Schedule',
        'description': "Unofficial Philippine Professional Regulation Commission\'s examination schedule",
        'link': 'https://api.whenisthenextboardexam.com/docs/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Represent by Open North',
        'description': 'Find Canadian Government Representatives',
        'link': 'https://represent.opennorth.ca/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'USAspending.gov',
        'description': 'US federal spending data',
        'link': 'https://api.usaspending.gov/',
        'https': True,
        'cors': 'unknown',
    },
]







def setup(bot):
    """Module setup - Government APIs loaded."""
    register_apis('government', APIS)
    bot.memory['government_loaded'] = True
    bot.memory['government_count'] = 67


def shutdown(bot):
    """Module shutdown."""
    bot.memory['government_loaded'] = False


@plugin.command('country_apicolombia')
@plugin.example('.country_apicolombia')
def country_apicolombia(bot, trigger):
    """Get information about Colombia using Api Colombia."""
    # Api Colombia: https://api-colombia.com/
    # Endpoint: GET https://api-colombia.com/api/v1/Country/Colombia

    logger.info('Api Colombia country lookup')

    url = 'https://api-colombia.com/api/v1/Country/Colombia'

    logger.debug(f'Fetching Colombia info: {url}')
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to fetch Colombia information.')
        return

    name = data.get('name', 'Colombia')
    description = data.get('description', '')
    population = data.get('population', 0)
    surface = data.get('surface', 0)
    time_zone = data.get('timeZone', '')

    response = f"{formatter.bold(name)}"
    if population:
        response += f" | Population: {formatter.bold(f'{population:,}')}"
    if surface:
        response += f" | Surface: {formatter.monospace(f'{surface:,} km²')}"
    if time_zone:
        response += f" | Timezone: {formatter.monospace(time_zone)}"
    if description:
        response += f" | {formatter.italic(description[:100])}"

    bot.say(formatter.truncate(response, max_len=400))
