"""
Sopel module for Science & Math APIs.
Supports 25 public APIs with no authentication required.
"""

import os
import sys

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, IRCFormatter, XMLParser, get_module_logger, register_apis

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)
formatter = IRCFormatter()

# API definitions
APIS = [
    {
        'name': 'arXiv',
        'description': 'Curated research-sharing platform: physics, mathematics, quantitative finance, and economics',
        'link': 'https://arxiv.org/help/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Bootprint',
        'description': 'Random facts and images of space',
        'link': 'https://bootprint.space/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'GBIF',
        'description': 'Global Biodiversity Information Facility',
        'link': 'https://www.gbif.org/developer/summary',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'iDigBio',
        'description': 'Access millions of museum specimens from organizations around the world',
        'link': 'https://github.com/idigbio/idigbio-search-api/wiki',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'inspirehep.net',
        'description': 'High Energy Physics info. system',
        'link': 'https://github.com/inspirehep/rest-api-doc',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'isEven (humor)',
        'description': 'Check if a number is even',
        'link': 'https://isevenapi.xyz/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'ISRO',
        'description': 'ISRO Space Crafts Information',
        'link': 'https://isro.vercel.app',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'ISRO Statistics',
        'description': 'ISRO Launches and Spacecrafts details',
        'link': 'https://isrostats.in/apis',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'ITIS',
        'description': 'Integrated Taxonomic Information System',
        'link': 'https://www.itis.gov/ws_description.html',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Launch Library 2',
        'description': 'Spaceflight launches and events database',
        'link': 'https://thespacedevs.com/llapi',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'NASA',
        'description': 'NASA data, including imagery',
        'link': 'https://api.nasa.gov',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Newton',
        'description': 'Symbolic and Arithmetic Math Calculator',
        'link': 'https://newton.vercel.app',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Noctua',
        'description': 'REST API used to access NoctuaSky features',
        'link': 'https://api.noctuasky.com/api/v1/swaggerdoc/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Numbers',
        'description': 'Facts about numbers',
        'link': 'http://numbersapi.com',
        'https': False,
        'cors': 'no',
    },
    {
        'name': 'Open Notify',
        'description': 'ISS astronauts, current location, etc',
        'link': 'http://open-notify.org/Open-Notify-API/',
        'https': False,
        'cors': 'no',
    },
    {
        'name': 'Purple Air',
        'description': 'Real Time Air Quality Monitoring',
        'link': 'https://www2.purpleair.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Satellite Passes',
        'description': 'Find satellite passes',
        'link': 'https://sat.terrestre.ar',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'SHARE',
        'description': 'A free, open, dataset about research and scholarly activities',
        'link': 'https://share.osf.io/api/v2/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'SpaceX',
        'description': 'Company, vehicle, launchpad and launch data',
        'link': 'https://github.com/r-spacex/SpaceX-API',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Sunrise and Sunset',
        'description': 'Sunset and sunrise times for a given latitude and longitude',
        'link': 'https://sunrise-sunset.org/api',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Times Adder',
        'description': 'With this API you can add each of the times introduced in the array sent',
        'link': 'https://github.com/FranP-code/API-Times-Adder',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'TLE',
        'description': 'Satellite information',
        'link': 'https://tle.ivanstanojevic.me',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'USGS Earthquake Hazards Program',
        'description': 'Earthquakes data real-time',
        'link': 'https://earthquake.usgs.gov/fdsnws/event/1/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'USGS Water Services',
        'description': 'Water quality and level info for rivers and lakes',
        'link': 'https://waterservices.usgs.gov/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'World Bank',
        'description': 'World Data',
        'link': 'https://datahelpdesk.worldbank.org/knowledgebase/topics/125589',
        'https': True,
        'cors': 'no',
    },
]


@plugin.command('arxiv')
@plugin.example('.arxiv quantum')
@plugin.example('.arxiv machine learning')
def arxiv_search(bot, trigger):
    """Search arXiv research papers."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .arxiv <search_query>')
        return

    query = trigger.group(2).strip()
    logger.info(f'ArXiv search: {query}')

    # arXiv API search - returns XML, not JSON
    encoded_query = http.quote(query)
    url = f'https://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results=3'

    logger.debug(f'Searching arXiv: {url}')

    try:
        # Use HTTPClient's get_text for XML response
        xml_data = http.get_text(url)

        if not xml_data:
            bot.notice(trigger.nick, f'No papers found for "{query}" or API error.')
            return

        # Parse XML using ElementTree
        root = XMLParser.parse_etree(xml_data)

        if root is None:
            bot.notice(trigger.nick, 'Failed to parse XML response.')
            return

        # Find all entry elements (arXiv returns Atom feed format)
        entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')

        if not entries:
            bot.notice(trigger.nick, f'No papers found for "{query}"')
            return

        bot.say(f'Found {len(entries)} paper(s) for "{query}":')
        for i, entry in enumerate(entries[:3], 1):
            # Extract title
            title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else 'Unknown'

            # Extract published date
            published_elem = entry.find('{http://www.w3.org/2005/Atom}published')
            published = published_elem.text[:10] if published_elem is not None and published_elem.text else 'Unknown'

            # Extract summary
            summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
            summary = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else ''
            summary_short = summary.replace('\n', ' ')[:100] if summary else ''

            # Extract authors
            authors = []
            for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                name_elem = author.find('{http://www.w3.org/2005/Atom}name')
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())

            response = f"{i}. {formatter.bold(title)} | Published: {formatter.monospace(published)}"
            if authors:
                authors_str = ', '.join(authors[:2])
                if len(authors) > 2:
                    authors_str += f' +{len(authors)-2}'
                response += f" | {formatter.italic(authors_str)}"
            bot.say(formatter.truncate(response, max_len=400))
            if summary_short:
                bot.say(f"   {formatter.italic(summary_short)}...")

    except Exception as e:
        logger.exception('Error searching arXiv', e)
        bot.notice(trigger.nick, 'Failed to search arXiv. Please try again.')

def setup(bot):
    """Module setup - Science & Math APIs loaded."""
    register_apis('science_math', APIS)
    bot.memory['science_math_loaded'] = True
    bot.memory['science_math_count'] = 25
    logger.info('Science & Math module loaded')

def shutdown(bot):
    """Module shutdown."""
    bot.memory['science_math_loaded'] = False
    logger.info('Science & Math module unloaded')
