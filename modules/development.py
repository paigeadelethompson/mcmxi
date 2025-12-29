"""
Sopel module for Development APIs.
Supports 52 public APIs with no authentication required.
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
        'name': '24 Pull Requests',
        'description': 'Project to promote open source collaboration during December',
        'link': 'https://24pullrequests.com/api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Abacus',
        'description': 'Free and simple counting service. You can use it to track page hits and specific events',
        'link': 'https://abacus.jasoncameron.dev/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Agify.io',
        'description': 'Estimates the age from a first name',
        'link': 'https://agify.io',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'API Grátis',
        'description': 'Multiples services and public APIs',
        'link': 'https://apigratis.com.br/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'ApicAgent',
        'description': 'Extract device details from user-agent string',
        'link': 'https://www.apicagent.com',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'APIs.guru',
        'description': 'Wikipedia for Web APIs, OpenAPI/Swagger specs for public APIs',
        'link': 'https://apis.guru/api-doc/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Beeceptor',
        'description': 'Build a mock Rest API endpoint in seconds',
        'link': 'https://beeceptor.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'CDNJS',
        'description': 'Library info on CDNJS',
        'link': 'https://api.cdnjs.com/libraries/jquery',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Ciprand',
        'description': 'Secure random string generator',
        'link': 'https://github.com/polarspetroll/ciprand',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Cloudflare Trace',
        'description': 'Get IP Address, Timestamp, User Agent, Country Code, IATA, HTTP Version, TLS/SSL Version & More',
        'link': 'https://github.com/fawazahmed0/cloudflare-trace-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Codex',
        'description': 'Online Compiler for Various Languages',
        'link': 'https://github.com/Jaagrav/CodeX',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'CORS Proxy',
        'description': 'Get around the dreaded CORS error by using this proxy as a middle man',
        'link': 'https://github.com/burhanuday/cors-proxy',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Corsfix',
        'description': 'Corsfix lets you fetch any resource and bypass CORS errors, free for development environment',
        'link': 'https://corsfix.com/docs/cors-proxy/api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'DigitalOcean Status',
        'description': 'Status of all DigitalOcean services',
        'link': 'https://status.digitalocean.com/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'DomainDb Info',
        'description': 'Domain name search to find all domains containing particular words/phrases/etc',
        'link': 'https://api.domainsdb.info/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'ExtendsClass JSON Storage',
        'description': 'A simple JSON store API',
        'link': 'https://extendsclass.com/json-storage.html',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Format JSON Online Dummy API',
        'description': '– A free tool to generate dummy JSON data for testing and prototyping.',
        'link': 'https://formatjsononline.com/dummy-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Genderize.io',
        'description': 'Estimates a gender from a first name',
        'link': 'https://genderize.io',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Hoppscotch',
        'description': 'A lightweight, fast, and customizable app for testing and designing APIs. A free, fast, and beautiful',
        'link': 'https://hoppscotch.io/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'HTTP2.Pro',
        'description': 'Test endpoints for client and server HTTP/2 protocol support',
        'link': 'https://http2.pro/doc/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'HTTPie',
        'description': 'a free command-line HTTP client for the API era',
        'link': 'https://httpie.io',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Httpbin',
        'description': 'A Simple HTTP Request & Response Service',
        'link': 'https://httpbin.org/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'IFTTT',
        'description': 'IFTTT Connect API',
        'link': 'https://platform.ifttt.com/docs/connect_api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Image-Charts',
        'description': 'Generate charts, QR codes and graph images',
        'link': 'https://documentation.image-charts.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'IPify',
        'description': 'A simple IP Address API',
        'link': 'https://www.ipify.org/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'IPinfo',
        'description': 'Another simple IP Address API',
        'link': 'https://ipinfo.io/developers',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'IPLocate',
        'description': 'IP geolocation and threat data API',
        'link': 'https://www.iplocate.io/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'IPQuery',
        'description': 'A free IP Geolocation and proxy/tor/VPN detection API',
        'link': 'https://ipquery.io',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'jsDelivr',
        'description': 'Package info and download stats on jsDelivr CDN',
        'link': 'https://github.com/jsdelivr/data.jsdelivr.com',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'JSON 2 JSONP',
        'description': 'Convert JSON to JSONP (on-the-fly) for easy cross-domain data requests using client-side JavaScript',
        'link': 'https://json2jsonp.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Kroki',
        'description': 'Creates diagrams from textual descriptions',
        'link': 'https://kroki.io',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'License-API',
        'description': 'Unofficial REST API for choosealicense.com',
        'link': 'https://github.com/cmccandless/license-api/blob/master/README.md',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Lua Decompiler',
        'description': 'Online Lua 5.1 Decompiler',
        'link': 'https://lua-decompiler.ferib.dev/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'MicroENV',
        'description': 'Fake Rest API for developers',
        'link': 'https://microenv.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Mocky',
        'description': 'Mock user defined test JSON for REST API endpoints',
        'link': 'https://designer.mocky.io/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'MY IP',
        'description': 'Get IP address information',
        'link': 'https://www.myip.com/api-docs/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'MySQL Visual EXPLAIN',
        'description': 'Transform MySQL EXPLAIN output to interactive graphs',
        'link': 'https://api.mysqlexplain.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Nationalize.io',
        'description': 'Estimate the nationality of a first name',
        'link': 'https://nationalize.io',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'NetworkCalc',
        'description': 'Network calculators, including subnets, DNS, binary, and security tools',
        'link': 'https://networkcalc.com/api/docs',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'npm Registry',
        'description': 'Query information about your favorite Node.js libraries programmatically',
        'link': 'https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'QR code',
        'description': 'Create an easy to read QR code and URL shortener',
        'link': 'https://www.qrtag.net/api/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'QR code',
        'description': 'Generate and decode / read QR code graphics',
        'link': 'http://goqr.me/api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Qrcode Monkey',
        'description': 'Integrate custom and unique looking QR codes into your system or workflow',
        'link': 'https://www.qrcode-monkey.com/qr-code-api-with-logo/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'QuickChart',
        'description': 'Generate chart and graph images',
        'link': 'https://quickchart.io/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'ReqRes',
        'description': 'A hosted REST-API ready to respond to your AJAX requests',
        'link': 'https://reqres.in/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'RSS to JSON',
        'description': 'Returns RSS feed in JSON format using feed URL',
        'link': 'https://github.com/ayusharma/RSS-to-JSON',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Serialif Color',
        'description': 'Color conversion, complementary, grayscale and contrasted text',
        'link': 'https://color.serialif.com/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Shadify',
        'description': 'Service for generating data and executing logic to create various games and puzzles',
        'link': 'https://github.com/cheatsnake/shadify',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Sonar',
        'description': 'Project Sonar DNS Enumeration API',
        'link': 'https://github.com/Cgboal/SonarSearch',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Statically',
        'description': 'A free CDN for developers',
        'link': 'https://statically.io/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Wandbox',
        'description': 'Code compiler supporting 35+ languages mentioned at wandbox.org',
        'link': 'https://github.com/melpon/wandbox/blob/master/kennel/API.md',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'YAMLine',
        'description': 'Convert YAML to JSON (on-the-fly)',
        'link': 'https://yamline.com/json/',
        'https': True,
        'cors': 'yes',
    },
]




@plugin.command('age_agify')
@plugin.example('.age_agify John')
def age_agify(bot, trigger):
    """Estimate age from a name using Agify.io."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .age_agify <name>')
        return

    name = trigger.group(2).strip()
    logger.info(f'Age lookup for: {name}')

    encoded_name = http.quote(name)
    url = f'https://api.agify.io?name={encoded_name}'
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to fetch age data. Please try again.')
        return

    age = data.get('age', 'Unknown')
    count = data.get('count', 0)

    response = f"Estimated age for {formatter.bold(name)}: {formatter.bold(str(age))} years"
    response += f" | Based on {formatter.monospace(f'{count:,}')} samples"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('trace_cloudflare')
@plugin.example('.trace_cloudflare')
def trace_cloudflare(bot, trigger):
    """Get connection info using Cloudflare Trace API."""
    logger.info('Fetching trace info')

    url = 'https://cloudflare-trace.com/'
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to fetch trace data.')
        return

    ip = data.get('ip', 'Unknown')
    country = data.get('country', 'Unknown')
    city = data.get('city', 'Unknown')
    http_version = data.get('httpVersion', 'Unknown')
    tls_version = data.get('tlsVersion', 'Unknown')

    response = f"IP: {formatter.bold(ip)} | Location: {formatter.italic(f'{city}, {country}')}"
    response += f" | HTTP: {formatter.monospace(http_version)}"
    if tls_version != 'Unknown':
        response += f" | TLS: {formatter.monospace(tls_version)}"

    bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Development APIs loaded."""
    register_apis('development', APIS)
    bot.memory['development_loaded'] = True
    bot.memory['development_count'] = 52
    logger.info('Development module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['development_loaded'] = False
    logger.info('Development module unloaded')


@plugin.command('library_cdnjs')
@plugin.example('.library_cdnjs jquery')
def library_cdnjs(bot, trigger):
    """Search for JavaScript libraries on CDNJS."""
    # CDNJS: https://api.cdnjs.com/libraries
    # Endpoint: GET https://api.cdnjs.com/libraries?search={query}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .library_cdnjs <library_name>')
        bot.notice(trigger.nick, 'Example: .library_cdnjs jquery')
        return

    query = trigger.group(2).strip()

    logger.info(f'CDNJS library search: {query}')

    encoded_query = http.quote(query)
    url = f'https://api.cdnjs.com/libraries?search={encoded_query}&fields=version,description,homepage'

    logger.debug(f'Searching CDNJS: {url}')
    data = http.get(url)

    if not data or 'results' not in data:
        bot.notice(trigger.nick, 'Failed to search CDNJS.')
        return

    results = data.get('results', [])

    if not results:
        bot.notice(trigger.nick, f'No libraries found for "{query}"')
        return

    bot.say(f'Found {len(results)} library/libraries for "{query}" (showing {min(3, len(results))}):')
    for lib in results[:3]:
        name = lib.get('name', 'Unknown')
        version = lib.get('version', 'Unknown')
        description = lib.get('description', '')
        latest = lib.get('latest', '')

        response = f"{formatter.bold(name)}"
        if version:
            response += f" v{formatter.monospace(version)}"
        if description:
            response += f" | {formatter.italic(description[:60])}"
        bot.say(formatter.truncate(response, max_len=400))
        if latest:
            bot.say(f"  {formatter.monospace(latest[:200])}")


@plugin.command('status_digitalocean')
@plugin.example('.status_digitalocean')
def status_digitalocean(bot, trigger):
    """Get DigitalOcean service status."""
    # DigitalOcean Status: https://status.digitalocean.com/api
    # Endpoint: GET https://status.digitalocean.com/api/v2/status.json

    logger.info('DigitalOcean status check')

    url = 'https://status.digitalocean.com/api/v2/status.json'

    logger.debug(f'Fetching status: {url}')
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to fetch DigitalOcean status.')
        return

    status = data.get('status', {})
    indicator = status.get('indicator', 'unknown')
    description = status.get('description', 'All Systems Operational')

    # Map indicator to status
    status_map = {
        'none': 'Operational',
        'minor': 'Minor Issues',
        'major': 'Major Issues',
        'critical': 'Critical Issues'
    }
    status_text = status_map.get(indicator, indicator)

    response = f"{formatter.bold('DigitalOcean Status')}: {formatter.bold(status_text)}"
    response += f" | {formatter.italic(description)}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('networkcalc_ip')
@plugin.example('.networkcalc_ip 192.168.1.1')
@plugin.example('.networkcalc_ip 192.168.1.0/24')
def networkcalc_ip(bot, trigger):
    """Calculate network information using NetworkCalc API."""
    # NetworkCalc: https://networkcalc.com/api/docs
    # Endpoint: GET https://networkcalc.com/api/ip/{ip_or_cidr}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .networkcalc_ip <ip_address> or <cidr>')
        bot.notice(trigger.nick, 'Examples: .networkcalc_ip 192.168.1.1')
        bot.notice(trigger.nick, '          .networkcalc_ip 192.168.1.0/24')
        return

    ip_or_cidr = trigger.group(2).strip()

    logger.info(f'NetworkCalc lookup: {ip_or_cidr}')

    encoded_ip = http.quote(ip_or_cidr)
    url = f'https://networkcalc.com/api/ip/{encoded_ip}'

    logger.debug(f'Calculating network: {url}')
    data = http.get(url)

    if not data or 'address' not in data:
        bot.notice(trigger.nick, 'Failed to calculate network information.')
        return

    address = data.get('address', {})
    cidr = address.get('cidr_notation', '')
    subnet_mask = address.get('subnet_mask', '')
    network = address.get('network_address', '')
    broadcast = address.get('broadcast_address', '')
    hosts = address.get('assignable_hosts', 0)

    response = f"{formatter.bold('NetworkCalc')} {formatter.monospace(cidr)}"
    if subnet_mask:
        response += f" | Subnet: {formatter.monospace(subnet_mask)}"
    if network:
        response += f" | Network: {formatter.monospace(network)}"
    if broadcast:
        response += f" | Broadcast: {formatter.monospace(broadcast)}"
    if hosts is not None:
        response += f" | Hosts: {formatter.bold(str(hosts))}"

    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('qr_goqr')
@plugin.example('.qr_goqr https://example.com')
def qr_goqr(bot, trigger):
    """Generate QR code URL using goqr.me API."""
    # QR code (goqr.me): http://goqr.me/api/
    # Endpoint: GET https://api.qrserver.com/v1/create-qr-code/?size={size}&data={data}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .qr_goqr <data>')
        bot.notice(trigger.nick, 'Example: .qr_goqr https://example.com')
        return

    data = trigger.group(2).strip()

    logger.info(f'QR code generation: {data[:50]}')

    encoded_data = http.quote(data)
    # Generate QR code URL (100x100 default size)
    qr_url = f'https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={encoded_data}'

    response = f"{formatter.bold('QR Code')} for {formatter.italic(data[:50])}:"
    bot.say(response)
    bot.say(f"{formatter.monospace(qr_url)}")


@plugin.command('ip_ipify')
@plugin.example('.ip_ipify')
def ip_ipify(bot, trigger):
    """Get your public IP address using IPify API."""
    # IPify: https://www.ipify.org/
    # Endpoint: GET https://api.ipify.org?format=json

    logger.info('IPify IP lookup')

    url = 'https://api.ipify.org?format=json'

    logger.debug(f'Fetching IP: {url}')
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to fetch IP address.')
        return

    ip = data.get('ip', 'Unknown')

    bot.say(f"Your IP: {formatter.bold(ip)}")


@plugin.command('gender_genderize')
@plugin.example('.gender_genderize john')
def gender_genderize(bot, trigger):
    """Estimate gender from a name using Genderize.io."""
    # Genderize.io: https://genderize.io
    # Endpoint: GET https://api.genderize.io?name={name}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .gender_genderize <name>')
        bot.notice(trigger.nick, 'Example: .gender_genderize john')
        return

    name = trigger.group(2).strip()

    logger.info(f'Genderize lookup for: {name}')

    encoded_name = http.quote(name)
    url = f'https://api.genderize.io?name={encoded_name}'

    logger.debug(f'Fetching gender: {url}')
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to fetch gender data.')
        return

    gender = data.get('gender', 'unknown')
    probability = data.get('probability', 0.0)
    count = data.get('count', 0)

    if gender:
        prob_pct = int(probability * 100)
        response = f"Name {formatter.bold(name)}: {formatter.bold(gender)}"
        response += f" ({prob_pct}% probability)"
        response += f" | Based on {formatter.monospace(f'{count:,}')} samples"
        bot.say(formatter.truncate(response, max_len=400))
    else:
        bot.say(f"Gender for {formatter.bold(name)}: {formatter.italic('unknown')}")


@plugin.command('nationality_nationalize')
@plugin.example('.nationality_nationalize michael')
def nationality_nationalize(bot, trigger):
    """Estimate nationality from a name using Nationalize.io."""
    # Nationalize.io: https://nationalize.io
    # Endpoint: GET https://api.nationalize.io?name={name}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .nationality_nationalize <name>')
        bot.notice(trigger.nick, 'Example: .nationality_nationalize michael')
        return

    name = trigger.group(2).strip()

    logger.info(f'Nationalize lookup for: {name}')

    encoded_name = http.quote(name)
    url = f'https://api.nationalize.io?name={encoded_name}'

    logger.debug(f'Fetching nationality: {url}')
    data = http.get(url)

    if not data or 'country' not in data:
        bot.notice(trigger.nick, 'Failed to fetch nationality data.')
        return

    countries = data.get('country', [])
    count = data.get('count', 0)

    if not countries:
        bot.say(f"Nationality for {formatter.bold(name)}: {formatter.italic('unknown')}")
        return

    # Show top 3 countries
    top_countries = []
    for country in countries[:3]:
        country_id = country.get('country_id', '')
        prob = country.get('probability', 0.0)
        prob_pct = int(prob * 100)
        top_countries.append(f"{formatter.bold(country_id)} ({prob_pct}%)")

    response = f"Name {formatter.bold(name)}: {', '.join(top_countries)}"
    response += f" | Based on {formatter.monospace(f'{count:,}')} samples"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('package_npm')
@plugin.example('.package_npm lodash')
@plugin.example('.package_npm express')
def package_npm(bot, trigger):
    """Query npm package information from npm Registry."""
    # npm Registry: https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md
    # Endpoint: GET https://registry.npmjs.org/{package}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .package_npm <package_name>')
        bot.notice(trigger.nick, 'Example: .package_npm lodash')
        return

    package_name = trigger.group(2).strip().lower()

    logger.info(f'npm package lookup: {package_name}')

    url = f'https://registry.npmjs.org/{http.quote(package_name)}'

    logger.debug(f'Fetching package info: {url}')
    data = http.get(url)

    if not data or 'name' not in data:
        bot.notice(trigger.nick, f'Package "{package_name}" not found.')
        return

    name = data.get('name', package_name)
    dist_tags = data.get('dist-tags', {})
    latest_version = dist_tags.get('latest', 'Unknown')
    description = data.get('description', '')

    # Get repository info
    repository = data.get('repository', {})
    repo_url = repository.get('url', '') if isinstance(repository, dict) else ''

    response = f"{formatter.bold(name)}"
    response += f" v{formatter.monospace(latest_version)}"
    if description:
        response += f" | {formatter.italic(description[:80])}"
    if repo_url:
        # Clean up git+ prefix
        clean_url = repo_url.replace('git+https://', 'https://').replace('git+ssh://', '').replace('.git', '')
        if clean_url:
            response += f" | {formatter.monospace(clean_url[:60])}"

    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('http_httpbin')
@plugin.example('.http_httpbin get')
@plugin.example('.http_httpbin ip')
def http_httpbin(bot, trigger):
    """Test HTTP endpoints using Httpbin.org."""
    # Httpbin: https://httpbin.org/
    # Endpoints: /get, /post, /ip, /headers, /user-agent, /status/{code}, etc.

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .http_httpbin <endpoint>')
        bot.notice(trigger.nick, 'Examples: .http_httpbin get')
        bot.notice(trigger.nick, '          .http_httpbin ip')
        bot.notice(trigger.nick, '          .http_httpbin headers')
        bot.notice(trigger.nick, 'Available: get, post, ip, headers, user-agent')
        return

    endpoint = trigger.group(2).strip().lower()

    # Valid endpoints
    valid_endpoints = ['get', 'post', 'ip', 'headers', 'user-agent', 'status']

    if endpoint not in valid_endpoints:
        bot.notice(trigger.nick, f'Invalid endpoint. Valid: {", ".join(valid_endpoints)}')
        return

    logger.info(f'Httpbin request: {endpoint}')

    url = f'https://httpbin.org/{endpoint}'

    logger.debug(f'Testing endpoint: {url}')
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, f'Failed to test endpoint: {endpoint}')
        return

    if endpoint == 'ip':
        origin = data.get('origin', 'Unknown')
        bot.say(f"{formatter.bold('Httpbin IP')}: {formatter.monospace(origin)}")
    elif endpoint == 'user-agent':
        user_agent = data.get('user-agent', 'Unknown')
        bot.say(f"{formatter.bold('Httpbin User-Agent')}: {formatter.monospace(user_agent[:100])}")
    elif endpoint == 'headers':
        headers = data.get('headers', {})
        # Show a few key headers
        key_headers = dict(list(headers.items())[:3])
        headers_str = ', '.join([f"{k}: {v[:30]}" for k, v in key_headers.items()])
        bot.say(f"{formatter.bold('Httpbin Headers')}: {formatter.monospace(headers_str[:200])}")
    elif endpoint == 'get':
        origin = data.get('origin', 'Unknown')
        url_req = data.get('url', '')
        bot.say(f"{formatter.bold('Httpbin GET')}: Origin {formatter.monospace(origin)}")
        bot.say(f"URL: {formatter.monospace(url_req[:150])}")
    else:
        # Generic response
        bot.say(f"{formatter.bold('Httpbin Response')} ({endpoint}): {formatter.monospace(str(data)[:200])}")
