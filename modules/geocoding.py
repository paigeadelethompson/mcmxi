"""
Sopel module for Geocoding APIs.
Supports 42 public APIs with no authentication required.
"""

import os
import sys

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import GraphQLClient, HTTPClient, IRCFormatter, get_module_logger, register_apis

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)
formatter = IRCFormatter()


# API definitions
APIS = [
    {
        'name': 'administrative-divisons-db',
        'description': 'Get all administrative divisions of a country',
        'link': 'https://github.com/kamikazechaser/administrative-divisions-db',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'adresse.data.gouv.fr',
        'description': 'Address database of France, geocoding and reverse',
        'link': 'https://adresse.data.gouv.fr',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': "BigDataCloud's Free API",
        'description': 'Get free client-side reverse geocoding API and Client Info API. No account creation and API key required.',
        'link': 'https://www.bigdatacloud.com//free-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'bng2latlong',
        'description': 'Convert British OSGB36 easting and northing (British National Grid) to WGS84 latitude and longitude',
        'link': 'https://www.getthedata.com/bng2latlong',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Cartes.io',
        'description': 'Create maps and markers for anything',
        'link': 'https://github.com/M-Media-Group/Cartes.io/wiki/API',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Cep.la',
        'description': 'Brazil RESTful API to find information about streets, zip codes, neighborhoods, cities and states',
        'link': 'http://cep.la/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'CitySDK',
        'description': 'Open APIs for select European cities',
        'link': 'http://www.citysdk.eu/citysdk-toolkit/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Country',
        'description': "Get your visitor's country from their IP",
        'link': 'http://country.is/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Ducks Unlimited',
        'description': 'API explorer that gives a query URL with a JSON response of locations and cities',
        'link': 'https://gis.ducks.org/datasets/du-university-chapters/api',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'FreeGeoIP',
        'description': 'Free geo ip information, no registration required. 15k/hour rate limit',
        'link': 'https://freegeoip.app/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'GeoApi',
        'description': 'French geographical data',
        'link': 'https://api.gouv.fr/api/geoapi.html',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Geocode.xyz',
        'description': 'Provides worldwide forward/reverse geocoding, batch geocoding and geoparsing',
        'link': 'https://geocode.xyz/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Geodata.gov.gr',
        'description': 'Open geospatial data and API service for Greece',
        'link': 'https://geodata.gov.gr/en/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'GeoDescription',
        'description': 'Reverse geocoding - Converting geographic coordinates to address-like location description',
        'link': 'https://geodescription.com',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'GeographQL',
        'description': 'A Country, State, and City GraphQL API',
        'link': 'https://geographql.netlify.app',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'GeoJS',
        'description': 'IP geolocation with ChatOps integration',
        'link': 'https://www.geojs.io/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Geokeo',
        'description': 'Geokeo geocoding service- with 2500 free api requests daily',
        'link': 'https://geokeo.com',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'GeoNames',
        'description': 'Place names and other geographical data',
        'link': 'http://www.geonames.org/export/web-services.html',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'geoPlugin',
        'description': 'IP geolocation and currency conversion',
        'link': 'https://www.geoplugin.com',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Graph Countries',
        'description': 'Country-related data like currencies, languages, flags, regions+subregions and bordering countries',
        'link': 'https://github.com/lennertVanSever/graphcountries',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'HelloSalut',
        'description': 'Get hello translation following user language',
        'link': 'https://fourtonfish.com/project/hellosalut-api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Hong Kong GeoData Store',
        'description': 'API for accessing geo-data of Hong Kong',
        'link': 'https://geodata.gov.hk/gs/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'IBGE',
        'description': 'Aggregate services of IBGE (Brazilian Institute of Geography and Statistics)',
        'link': 'https://servicodados.ibge.gov.br/api/docs/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'IP 2 Country',
        'description': 'Map an IP to a country',
        'link': 'https://ip2country.info',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'IP Address Details',
        'description': 'Find geolocation with ip address',
        'link': 'https://ipinfo.io/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'ip-api',
        'description': 'Find location with IP address or domain',
        'link': 'https://ip-api.com/docs',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'ipapi.co',
        'description': 'Find IP address location information',
        'link': 'https://ipapi.co/api/#introduction',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'IPGEO',
        'description': 'Unlimited free IP Address API with useful information',
        'link': 'https://api.techniknews.net/ipgeo/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Mexico',
        'description': 'Mexico RESTful zip codes API',
        'link': 'https://github.com/IcaliaLabs/sepomex',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Nominatim',
        'description': 'Provides worldwide forward / reverse geocoding',
        'link': 'https://nominatim.org/release-docs/latest/api/Overview/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'OnWater',
        'description': 'Determine if a lat/lon is on water or land',
        'link': 'https://onwater.io/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Open Topo Data',
        'description': 'Elevation and ocean depth for a latitude and longitude',
        'link': 'https://www.opentopodata.org',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'OpenPLZ API',
        'description': 'A public street and postal code directory for Austria, Germany, Liechtenstein and Switzerland via an open REST API',
        'link': 'https://www.openplzapi.org/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Pinball Map',
        'description': 'A crowdsourced map of public pinball machines',
        'link': 'https://pinballmap.com/api/v1/docs',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Postali',
        'description': 'Mexico Zip Codes API',
        'link': 'https://postali.app/api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Postcodes.io',
        'description': 'Postcode lookup & Geolocation for the UK',
        'link': 'https://postcodes.io',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'REST Countries',
        'description': 'Get information about countries via a RESTful API',
        'link': 'https://restcountries.com',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Rwanda Locations',
        'description': 'Rwanda Provinces, Districts, Cities, Capital City, Sector, cells, villages and streets',
        'link': 'https://rapidapi.com/victorkarangwa4/api/rwanda',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'SLF',
        'description': 'German city, country, river, database',
        'link': 'https://github.com/slftool/slftool.github.io/blob/master/API.md',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'ViaCep',
        'description': 'Brazil RESTful zip codes API',
        'link': 'https://viacep.com.br',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Zippopotam.us',
        'description': 'Get information about place such as country, city, state, etc',
        'link': 'http://www.zippopotam.us',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Ziptastic',
        'description': 'Get the country, state, and city of any US zip-code',
        'link': 'https://ziptasticapi.com/',
        'https': True,
        'cors': 'unknown',
    },
]




@plugin.command('geo_country')
@plugin.example('`geo_country')
def geo_country(bot, trigger):
    """Get country information from IP using Country API."""
    logger.info('Fetching country info from IP')

    url = 'https://api.country.is/'
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to fetch country data.')
        return

    country = data.get('country', 'Unknown')
    ip = data.get('ip', 'Unknown')

    response = f"IP: {formatter.monospace(ip)} | Country: {formatter.bold(country)}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('geo_geographql')
@plugin.example('`geo_geographql countries')
@plugin.example('`geo_geographql country code:US')
@plugin.example('`geo_geographql states country:US')
@plugin.example('`geo_geographql cities state:California country:US')
def geo_geographql(bot, trigger):
    """Query geographic data using GeographQL API."""
    # GeographQL: https://geographql.netlify.app
    # Endpoint: https://api.geographql.rudio.dev/graphql

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `geo_geographql <type> [options]')
        bot.notice(trigger.nick, 'Types: countries, country, states, cities')
        bot.notice(trigger.nick, 'Examples: .geo_geographql countries')
        bot.notice(trigger.nick, '          .geo_geographql country code:US')
        bot.notice(trigger.nick, '          .geo_geographql states country:US')
        bot.notice(trigger.nick, '          .geo_geographql cities state:California country:US')
        return

    query_parts = trigger.group(2).strip().split()
    query_type = query_parts[0].lower()

    # Parse options
    options = {}
    limit = 10
    for part in query_parts[1:]:
        if ':' in part:
            key, value = part.split(':', 1)
            options[key.lower()] = value
            if key.lower() == 'limit':
                try:
                    limit = int(value)
                    if limit < 1 or limit > 50:
                        limit = 10
                except ValueError:
                    limit = 10

    logger.info(f'GeographQL query: {query_type}, options: {options}')

    gql_client = GraphQLClient('https://api.geographql.rudio.dev/graphql')

    if query_type == 'countries':
        # List all countries
        query = """
        query GetCountries($first: Int!) {
            countries(first: $first) {
                edges {
                    node {
                        code
                        name
                    }
                }
            }
        }
        """
        result = gql_client.execute(query, {'first': limit})

        if result and 'countries' in result:
            countries = result.get('countries', {}).get('edges', [])
            if not countries:
                bot.notice(trigger.nick, 'No countries found.')
                return

            bot.say(f'Countries (showing {len(countries)}):')
            for edge in countries[:limit]:
                node = edge.get('node', {})
                code = node.get('code', '')
                name = node.get('name', 'Unknown')
                response = f"{formatter.bold(name)} ({formatter.monospace(code)})"
                bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, 'Failed to fetch countries.')

    elif query_type == 'country':
        # Get single country by code
        country_code = options.get('code', '').upper()
        if not country_code:
            bot.notice(trigger.nick, 'Usage: `geo_geographql country code:<country_code>')
            bot.notice(trigger.nick, 'Example: `geo_geographql country code:US')
            return

        query = """
        query GetCountry($code: ID!) {
            country(code: $code) {
                code
                name
                capital
                currency
                states {
                    code
                    name
                }
            }
        }
        """
        result = gql_client.execute(query, {'code': country_code})

        if result and 'country' in result:
            country = result.get('country')
            if not country:
                bot.notice(trigger.nick, f'Country with code "{country_code}" not found.')
                return

            name = country.get('name', 'Unknown')
            code = country.get('code', country_code)
            capital = country.get('capital', '')
            currency = country.get('currency', '')
            states = country.get('states', [])

            response = f"{formatter.bold(name)} ({formatter.monospace(code)})"
            if capital:
                response += f" | Capital: {formatter.italic(capital)}"
            if currency:
                response += f" | Currency: {formatter.monospace(currency)}"
            if states:
                response += f" | States: {formatter.bold(str(len(states)))}"
            bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, f'Failed to fetch country "{country_code}".')

    elif query_type == 'states':
        # Get states for a country
        country_code = options.get('country', '').upper()
        if not country_code:
            bot.notice(trigger.nick, 'Usage: `geo_geographql states country:<country_code>')
            bot.notice(trigger.nick, 'Example: `geo_geographql states country:US')
            return

        query = """
        query GetStates($code: ID!) {
            country(code: $code) {
                name
                states {
                    code
                    name
                }
            }
        }
        """
        result = gql_client.execute(query, {'code': country_code})

        if result and 'country' in result:
            country = result.get('country')
            if not country:
                bot.notice(trigger.nick, f'Country "{country_code}" not found.')
                return

            country_name = country.get('name', country_code)
            states = country.get('states', [])
            if not states:
                bot.notice(trigger.nick, f'No states found for {country_name}.')
                return

            bot.say(f'States in {formatter.bold(country_name)} (showing {min(limit, len(states))}):')
            for state in states[:limit]:
                code = state.get('code', '')
                name = state.get('name', 'Unknown')
                response = f"{formatter.bold(name)}"
                if code:
                    response += f" ({formatter.monospace(code)})"
                bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, f'Failed to fetch states for country "{country_code}".')

    elif query_type == 'cities':
        # Get cities for a state/country
        country_code = options.get('country', '').upper()
        state_name = options.get('state', '')

        if not country_code:
            bot.notice(trigger.nick, 'Usage: `geo_geographql cities country:<code> [state:<name>]')
            bot.notice(trigger.nick, 'Example: `geo_geographql cities country:US state:California')
            return

        query = """
        query GetCities($code: ID!) {
            country(code: $code) {
                name
                states {
                    name
                    cities {
                        name
                        latitude
                        longitude
                    }
                }
            }
        }
        """
        result = gql_client.execute(query, {'code': country_code})

        if result and 'country' in result:
            country = result.get('country')
            if not country:
                bot.notice(trigger.nick, f'Country "{country_code}" not found.')
                return

            country_name = country.get('name', country_code)
            states = country.get('states', [])

            # Filter by state if specified
            if state_name:
                states = [s for s in states if state_name.lower() in s.get('name', '').lower()]

            if not states:
                bot.notice(trigger.nick, 'No states found matching criteria.')
                return

            state = states[0]
            state_name_actual = state.get('name', 'Unknown')
            cities = state.get('cities', [])

            if not cities:
                bot.notice(trigger.nick, f'No cities found for {state_name_actual}.')
                return

            bot.say(f'Cities in {formatter.bold(state_name_actual)}, {country_name} (showing {min(limit, len(cities))}):')
            for city in cities[:limit]:
                name = city.get('name', 'Unknown')
                lat = city.get('latitude', '')
                lon = city.get('longitude', '')
                response = f"{formatter.bold(name)}"
                if lat and lon:
                    response += f" | {formatter.monospace(f'{lat}, {lon}')}"
                bot.say(formatter.truncate(response, max_len=400))
        else:
            bot.notice(trigger.nick, 'Failed to fetch cities.')

    else:
        bot.notice(trigger.nick, f'Unknown query type: {query_type}. Use: countries, country, states, or cities')


@plugin.command('geo_ipapi')
@plugin.example('`geo_ipapi')
@plugin.example('`geo_ipapi 8.8.8.8')
def geo_ipapi(bot, trigger):
    """Get IP geolocation using ip-api.com. Usage: `geo_ipapi [ip_address]"""
    ip = trigger.group(2).strip() if trigger.group(2) else ''
    
    # ip-api.com endpoint
    if ip:
        url = f'http://ip-api.com/json/{ip}'
    else:
        url = 'http://ip-api.com/json/'
    
    logger.info(f'Fetching IP geolocation from ip-api.com: {ip or "own IP"}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to fetch IP geolocation data.')
        return
    
    if data.get('status') == 'fail':
        bot.notice(trigger.nick, f"Error: {data.get('message', 'Unknown error')}")
        return
    
    ip_addr = data.get('query', 'Unknown')
    country = data.get('country', 'Unknown')
    region = data.get('regionName', '')
    city = data.get('city', '')
    isp = data.get('isp', '')
    org = data.get('org', '')
    lat = data.get('lat', '')
    lon = data.get('lon', '')
    timezone = data.get('timezone', '')
    
    response_parts = [f"IP: {formatter.monospace(ip_addr)}"]
    if country:
        response_parts.append(f"Country: {formatter.bold(country)}")
    if region:
        response_parts.append(f"Region: {formatter.italic(region)}")
    if city:
        response_parts.append(f"City: {formatter.italic(city)}")
    
    bot.say(formatter.truncate(' | '.join(response_parts), max_len=400))
    
    if lat and lon:
        bot.say(formatter.truncate(f"Coordinates: {formatter.monospace(f'{lat}, {lon}')}", max_len=400))
    if isp:
        bot.say(formatter.truncate(f"ISP: {formatter.monospace(isp)}", max_len=400))
    if org and org != isp:
        bot.say(formatter.truncate(f"Org: {formatter.monospace(org)}", max_len=400))
    if timezone:
        bot.say(formatter.truncate(f"Timezone: {formatter.monospace(timezone)}", max_len=400))


@plugin.command('geo_ipinfo')
@plugin.example('`geo_ipinfo')
@plugin.example('`geo_ipinfo 8.8.8.8')
def geo_ipinfo(bot, trigger):
    """Get IP address details using ipinfo.io. Usage: `geo_ipinfo [ip_address]"""
    ip = trigger.group(2).strip() if trigger.group(2) else ''
    
    # ipinfo.io endpoint
    if ip:
        url = f'https://ipinfo.io/{ip}/json'
    else:
        url = 'https://ipinfo.io/json'
    
    logger.info(f'Fetching IP info from ipinfo.io: {ip or "own IP"}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to fetch IP info.')
        return
    
    if 'error' in data:
        bot.notice(trigger.nick, f"Error: {data.get('error', {}).get('title', 'Unknown error')}")
        return
    
    ip_addr = data.get('ip', 'Unknown')
    city = data.get('city', '')
    region = data.get('region', '')
    country = data.get('country', '')
    loc = data.get('loc', '')  # lat,lon
    org = data.get('org', '')
    postal = data.get('postal', '')
    timezone = data.get('timezone', '')
    
    response_parts = [f"IP: {formatter.monospace(ip_addr)}"]
    if city:
        response_parts.append(f"City: {formatter.italic(city)}")
    if region:
        response_parts.append(f"Region: {formatter.italic(region)}")
    if country:
        response_parts.append(f"Country: {formatter.bold(country)}")
    
    bot.say(formatter.truncate(' | '.join(response_parts), max_len=400))
    
    if loc:
        bot.say(formatter.truncate(f"Coordinates: {formatter.monospace(loc)}", max_len=400))
    if org:
        bot.say(formatter.truncate(f"Org: {formatter.monospace(org)}", max_len=400))
    if postal:
        bot.say(formatter.truncate(f"Postal: {formatter.monospace(postal)}", max_len=400))
    if timezone:
        bot.say(formatter.truncate(f"Timezone: {formatter.monospace(timezone)}", max_len=400))


@plugin.command('geo_ipapi_co')
@plugin.example('`geo_ipapi_co')
@plugin.example('`geo_ipapi_co 8.8.8.8')
def geo_ipapi_co(bot, trigger):
    """Get IP geolocation using ipapi.co. Usage: `geo_ipapi_co [ip_address]"""
    ip = trigger.group(2).strip() if trigger.group(2) else ''
    
    # ipapi.co endpoint
    if ip:
        url = f'https://ipapi.co/{ip}/json/'
    else:
        url = 'https://ipapi.co/json/'
    
    logger.info(f'Fetching IP geolocation from ipapi.co: {ip or "own IP"}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to fetch IP geolocation data.')
        return
    
    if 'error' in data:
        bot.notice(trigger.nick, f"Error: {data.get('reason', 'Unknown error')}")
        return
    
    ip_addr = data.get('ip', 'Unknown')
    city = data.get('city', '')
    region = data.get('region', '')
    country_name = data.get('country_name', '')
    country_code = data.get('country_code', '')
    lat = data.get('latitude', '')
    lon = data.get('longitude', '')
    org = data.get('org', '')
    timezone = data.get('timezone', '')
    postal = data.get('postal', '')
    
    response_parts = [f"IP: {formatter.monospace(ip_addr)}"]
    if city:
        response_parts.append(f"City: {formatter.italic(city)}")
    if region:
        response_parts.append(f"Region: {formatter.italic(region)}")
    if country_name:
        response_parts.append(f"Country: {formatter.bold(country_name)}")
    if country_code:
        response_parts.append(f"({formatter.monospace(country_code)})")
    
    bot.say(formatter.truncate(' | '.join(response_parts), max_len=400))
    
    if lat and lon:
        bot.say(formatter.truncate(f"Coordinates: {formatter.monospace(f'{lat}, {lon}')}", max_len=400))
    if org:
        bot.say(formatter.truncate(f"Org: {formatter.monospace(org)}", max_len=400))
    if postal:
        bot.say(formatter.truncate(f"Postal: {formatter.monospace(postal)}", max_len=400))
    if timezone:
        bot.say(formatter.truncate(f"Timezone: {formatter.monospace(timezone)}", max_len=400))


@plugin.command('geo_nominatim')
@plugin.example('`geo_nominatim Seattle')
@plugin.example('`geo_nominatim reverse 47.6062 -122.3321')
def geo_nominatim(bot, trigger):
    """Geocode address or reverse geocode coordinates using Nominatim (OpenStreetMap).
    Usage: `geo_nominatim <address> | .geo_nominatim reverse <lat> <lon>
    """
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `geo_nominatim <address>')
        bot.notice(trigger.nick, '       `geo_nominatim reverse <lat> <lon>')
        return
    
    args = trigger.group(2).strip().split(None, 1)
    mode = args[0].lower()
    
    if mode == 'reverse':
        if len(args) < 2:
            bot.notice(trigger.nick, 'Usage: `geo_nominatim reverse <lat> <lon>')
            return
        try:
            coords = args[1].split()
            if len(coords) < 2:
                bot.notice(trigger.nick, 'Usage: `geo_nominatim reverse <lat> <lon>')
                return
            lat = float(coords[0])
            lon = float(coords[1])
        except ValueError:
            bot.notice(trigger.nick, 'Invalid coordinates. Use numbers for lat and lon.')
            return
        
        url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json'
        logger.info(f'Reverse geocoding with Nominatim: {lat}, {lon}')
    else:
        # Forward geocoding
        query = trigger.group(2).strip()
        url = f'https://nominatim.openstreetmap.org/search?q={http.quote(query)}&format=json&limit=1'
        logger.info(f'Geocoding with Nominatim: {query}')
    
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to fetch geocoding data.')
        return
    
    if mode == 'reverse':
        # Reverse geocoding response
        display_name = data.get('display_name', '')
        address = data.get('address', {})
        
        if not display_name:
            bot.notice(trigger.nick, 'No address found for those coordinates.')
            return
        
        response_parts = [formatter.bold(display_name)]
        if address.get('country'):
            response_parts.append(f"Country: {formatter.monospace(address['country'])}")
        
        bot.say(formatter.truncate(' | '.join(response_parts), max_len=400))
    else:
        # Forward geocoding response
        if isinstance(data, list) and len(data) > 0:
            result = data[0]
            display_name = result.get('display_name', '')
            lat = result.get('lat', '')
            lon = result.get('lon', '')
            
            if not display_name:
                bot.notice(trigger.nick, 'No results found.')
                return
            
            response_parts = [formatter.bold(display_name)]
            if lat and lon:
                response_parts.append(f"Coordinates: {formatter.monospace(f'{lat}, {lon}')}")
            
            bot.say(formatter.truncate(' | '.join(response_parts), max_len=400))
        else:
            bot.notice(trigger.nick, 'No results found.')


@plugin.command('geo_geocode_xyz')
@plugin.example('`geo_geocode_xyz Seattle')
@plugin.example('`geo_geocode_xyz reverse 47.6062 -122.3321')
def geo_geocode_xyz(bot, trigger):
    """Geocode address or reverse geocode coordinates using geocode.xyz.
    Usage: `geo_geocode_xyz <address> | .geo_geocode_xyz reverse <lat> <lon>
    """
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `geo_geocode_xyz <address>')
        bot.notice(trigger.nick, '       `geo_geocode_xyz reverse <lat> <lon>')
        return
    
    args = trigger.group(2).strip().split(None, 1)
    mode = args[0].lower()
    
    if mode == 'reverse':
        if len(args) < 2:
            bot.notice(trigger.nick, 'Usage: `geo_geocode_xyz reverse <lat> <lon>')
            bot.notice(trigger.nick, '       `geo_geocode_xyz reverse <lat>, <lon>')
            return
        try:
            # Handle both space-separated and comma-separated formats
            coords_str = args[1].strip()
            # Replace comma with space, then split
            coords = coords_str.replace(',', ' ').split()
            if len(coords) < 2:
                bot.notice(trigger.nick, 'Usage: `geo_geocode_xyz reverse <lat> <lon>')
                bot.notice(trigger.nick, '       `geo_geocode_xyz reverse <lat>, <lon>')
                return
            lat = float(coords[0])
            lon = float(coords[1])
        except ValueError:
            bot.notice(trigger.nick, 'Invalid coordinates. Use numbers for lat and lon.')
            return
        
        url = f'https://geocode.xyz/{lat},{lon}?json=1'
        logger.info(f'Reverse geocoding with geocode.xyz: {lat}, {lon}')
    else:
        # Forward geocoding
        query = trigger.group(2).strip()
        url = f'https://geocode.xyz/{http.quote(query)}?json=1'
        logger.info(f'Geocoding with geocode.xyz: {query}')
    
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to fetch geocoding data.')
        return
    
    error = data.get('error', {})
    if error:
        bot.notice(trigger.nick, f"Error: {error.get('description', 'Unknown error')}")
        return
    
    if mode == 'reverse':
        # Reverse geocoding response
        standard = data.get('standard', {})
        city = standard.get('city', '')
        prov = standard.get('prov', '')
        countryname = standard.get('countryname', '')
        postal = standard.get('postal', '')
        stnumber = standard.get('stnumber', '')
        staddress = standard.get('staddress', '')
        region = standard.get('region', '')
        
        response_parts = []
        # Street address
        if stnumber and staddress:
            response_parts.append(
                f"{formatter.bold(f'{stnumber} {staddress}')}"
            )
        elif staddress:
            response_parts.append(f"{formatter.bold(staddress)}")
        if city:
            response_parts.append(f"City: {formatter.italic(city)}")
        # Use region for state if available, otherwise prov
        if region:
            response_parts.append(f"State: {formatter.italic(region)}")
        elif prov and prov != 'US':  # Skip if prov is just country code
            response_parts.append(f"State: {formatter.italic(prov)}")
        if countryname:
            response_parts.append(f"Country: {formatter.bold(countryname)}")
        if postal:
            response_parts.append(f"Postal: {formatter.monospace(postal)}")
        
        if response_parts:
            bot.say(formatter.truncate(' | '.join(response_parts), max_len=400))
        else:
            bot.notice(trigger.nick, 'No address found for those coordinates.')
    else:
        # Forward geocoding response
        standard = data.get('standard', {})
        city = standard.get('city', '')
        prov = standard.get('prov', '')
        countryname = standard.get('countryname', '')
        lat = data.get('latt', '')
        longt = data.get('longt', '')
        
        response_parts = []
        if city:
            response_parts.append(f"City: {formatter.italic(city)}")
        if prov:
            response_parts.append(f"Province: {formatter.italic(prov)}")
        if countryname:
            response_parts.append(f"Country: {formatter.bold(countryname)}")
        if lat and longt:
            response_parts.append(f"Coordinates: {formatter.monospace(f'{lat}, {longt}')}")
        
        if response_parts:
            bot.say(formatter.truncate(' | '.join(response_parts), max_len=400))
        else:
            bot.notice(trigger.nick, 'No results found.')


@plugin.command('geo_onwater')
@plugin.example('`geo_onwater 47.6062 -122.3321')
def geo_onwater(bot, trigger):
    """Check if coordinates are on water or land using OnWater API.
    Usage: `geo_onwater <lat> <lon>
    """
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `geo_onwater <lat> <lon>')
        bot.notice(trigger.nick, 'Example: `geo_onwater 47.6062 -122.3321')
        return
    
    try:
        coords = trigger.group(2).strip().split()
        if len(coords) < 2:
            bot.notice(trigger.nick, 'Usage: `geo_onwater <lat> <lon>')
            return
        lat = float(coords[0])
        lon = float(coords[1])
    except ValueError:
        bot.notice(trigger.nick, 'Invalid coordinates. Use numbers for lat and lon.')
        return
    
    url = f'https://api.onwater.io/api/v1/results/{lat},{lon}'
    logger.info(f'Checking onwater.io: {lat}, {lon}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to fetch onwater data.')
        return
    
    water = data.get('water', False)
    lat_resp = data.get('lat', lat)
    lon_resp = data.get('lon', lon)
    
    location_type = formatter.bold('WATER') if water else formatter.bold('LAND')
    response = f"Coordinates {formatter.monospace(f'{lat_resp}, {lon_resp}')} are on {location_type}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('geo_geojs')
@plugin.example('`geo_geojs')
@plugin.example('`geo_geojs 8.8.8.8')
def geo_geojs(bot, trigger):
    """Get IP geolocation using GeoJS. Usage: `geo_geojs [ip_address]"""
    ip = trigger.group(2).strip() if trigger.group(2) else ''
    
    # GeoJS endpoint
    if ip:
        url = f'https://get.geojs.io/v1/ip/geo/{ip}.json'
    else:
        url = 'https://get.geojs.io/v1/ip/geo.json'
    
    logger.info(f'Fetching IP geolocation from GeoJS: {ip or "own IP"}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to fetch IP geolocation data.')
        return
    
    # GeoJS returns a list or single object
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
    
    ip_addr = data.get('ip', 'Unknown')
    country = data.get('country', '')
    region = data.get('region', '')
    city = data.get('city', '')
    latitude = data.get('latitude', '')
    longitude = data.get('longitude', '')
    organization = data.get('organization', '')
    timezone = data.get('timezone', '')
    
    response_parts = [f"IP: {formatter.monospace(ip_addr)}"]
    if city:
        response_parts.append(f"City: {formatter.italic(city)}")
    if region:
        response_parts.append(f"Region: {formatter.italic(region)}")
    if country:
        response_parts.append(f"Country: {formatter.bold(country)}")
    
    bot.say(formatter.truncate(' | '.join(response_parts), max_len=400))
    
    if latitude and longitude:
        bot.say(formatter.truncate(f"Coordinates: {formatter.monospace(f'{latitude}, {longitude}')}", max_len=400))
    if organization:
        bot.say(formatter.truncate(f"Org: {formatter.monospace(organization)}", max_len=400))
    if timezone:
        bot.say(formatter.truncate(f"Timezone: {formatter.monospace(timezone)}", max_len=400))


@plugin.command('geo_freegeoip')
@plugin.example('`geo_freegeoip')
@plugin.example('`geo_freegeoip 8.8.8.8')
def geo_freegeoip(bot, trigger):
    """Get IP geolocation using FreeGeoIP. Usage: `geo_freegeoip [ip_address]"""
    ip = trigger.group(2).strip() if trigger.group(2) else ''
    
    # FreeGeoIP endpoint
    if ip:
        url = f'https://freegeoip.app/json/{ip}'
    else:
        url = 'https://freegeoip.app/json/'
    
    logger.info(f'Fetching IP geolocation from FreeGeoIP: {ip or "own IP"}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to fetch IP geolocation data.')
        return
    
    ip_addr = data.get('ip', 'Unknown')
    country_name = data.get('country_name', '')
    country_code = data.get('country_code', '')
    region_name = data.get('region_name', '')
    city = data.get('city', '')
    latitude = data.get('latitude', '')
    longitude = data.get('longitude', '')
    time_zone = data.get('time_zone', '')
    
    response_parts = [f"IP: {formatter.monospace(ip_addr)}"]
    if city:
        response_parts.append(f"City: {formatter.italic(city)}")
    if region_name:
        response_parts.append(f"Region: {formatter.italic(region_name)}")
    if country_name:
        response_parts.append(f"Country: {formatter.bold(country_name)}")
    if country_code:
        response_parts.append(f"({formatter.monospace(country_code)})")
    
    bot.say(formatter.truncate(' | '.join(response_parts), max_len=400))
    
    if latitude and longitude:
        bot.say(formatter.truncate(f"Coordinates: {formatter.monospace(f'{latitude}, {longitude}')}", max_len=400))
    if time_zone:
        bot.say(formatter.truncate(f"Timezone: {formatter.monospace(time_zone)}", max_len=400))


def setup(bot):
    """Module setup - Geocoding APIs loaded."""
    register_apis('geocoding', APIS)
    bot.memory['geocoding_loaded'] = True
    bot.memory['geocoding_count'] = 42
    logger.info('Geocoding module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['geocoding_loaded'] = False
    logger.info('Geocoding module unloaded')
