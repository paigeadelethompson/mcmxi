"""
Sopel module for Security APIs.
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
        'name': 'Classify',
        'description': 'Encrypting & decrypting text messages',
        'link': 'https://github.com/cheatsnake/classify',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'EmailRep',
        'description': 'Email address threat and risk prediction',
        'link': 'https://docs.emailrep.io/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Escape',
        'description': 'An API for escaping different kind of queries',
        'link': 'https://github.com/polarspetroll/EscapeAPI',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'FilterLists',
        'description': 'Lists of filters for adblockers and firewalls',
        'link': 'https://api.filterlists.com',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Microsoft Security Response Center (MSRC)',
        'description': 'Programmatic interfaces to engage with the Microsoft Security Response Center (MSRC)',
        'link': 'https://msrc.microsoft.com/report/developer',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Mozilla http scanner',
        'description': 'Mozilla observatory http scanner',
        'link': 'https://github.com/mozilla/http-observatory/blob/master/httpobs/docs/api.md',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Mozilla tls scanner',
        'description': 'Mozilla observatory tls scanner',
        'link': 'https://github.com/mozilla/tls-observatory#api-endpoints',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'National Vulnerability Database',
        'description': 'U.S. National Vulnerability Database',
        'link': 'https://nvd.nist.gov/vuln/Data-Feeds/JSON-feed-changelog',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'OWASP ZAP',
        'description': 'Automated security testing API for web apps',
        'link': 'https://www.zaproxy.org/docs/api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Passwordinator',
        'description': 'Generate random passwords of varying complexities',
        'link': 'https://github.com/fawazsullia/password-generator/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'PhishStats',
        'description': 'Phishing database',
        'link': 'https://phishstats.info/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'UK Police',
        'description': 'UK Police data',
        'link': 'https://data.police.uk/docs/',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('security')
@plugin.command('security')
@plugin.example(f'.security')
def security_list(bot, trigger):
    """List all available Security APIs."""
    bot.say(f'Available Security APIs (12):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .security_info <name> for details')


@plugin.command('security_info')
@plugin.example(f'.security_info <name>')
def security_info(bot, trigger):
    """Get information about a specific Security API."""
    if not trigger.group(2):
        bot.say(f'Usage: .security_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('security_search')
@plugin.example(f'.security_search <query>')
def security_search(bot, trigger):
    """Search Security APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .security_search <query>')
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
    """Module setup - Security APIs loaded."""
    bot.memory['security_loaded'] = True
    bot.memory['security_count'] = 12


def shutdown(bot):
    """Module shutdown."""
    bot.memory['security_loaded'] = False




@plugin.command('password_passwordinator')
@plugin.require_privmsg('This command only works in private messages.')
@plugin.example('.password_passwordinator')
@plugin.example('.password_passwordinator 16')
def password_passwordinator(bot, trigger):
    """Generate a random secure password using Passwordinator API (private message only)."""
    # Passwordinator: https://github.com/fawazsullia/password-generator/
    # Endpoint: GET https://passwordinator.herokuapp.com/generate?length={length}
    
    length = 16  # default
    if trigger.group(2):
        try:
            length = int(trigger.group(2).strip())
            if length < 8 or length > 128:
                bot.notice(trigger.nick, 'Password length must be between 8 and 128 characters.')
                return
        except ValueError:
            bot.notice(trigger.nick, 'Invalid length. Please provide a number.')
            return
    
    logger.info(f'Generating password: length={length}')
    
    url = f'https://passwordinator.herokuapp.com/generate?length={length}'
    
    logger.debug(f'Generating password: {url}')
    data = http.get(url)
    
    if not data or 'password' not in data:
        bot.notice(trigger.nick, 'Failed to generate password.')
        return
    
    password = data.get('password', '')
    
    bot.notice(trigger.nick, f'Generated password (length {length}): {formatter.monospace(password)}')


@plugin.command('cve_nvd')
@plugin.example('.cve_nvd CVE-2024-0001')
@plugin.example('.cve_nvd search python')
def cve_nvd(bot, trigger):
    """Search National Vulnerability Database (NVD) for CVE information."""
    # National Vulnerability Database: https://nvd.nist.gov/vuln/Data-Feeds/JSON-feed-changelog
    # Endpoint: GET https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={query}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .cve_nvd <CVE_ID> or .cve_nvd search <keyword>')
        bot.notice(trigger.nick, 'Examples: .cve_nvd CVE-2024-0001')
        bot.notice(trigger.nick, '          .cve_nvd search python')
        return
    
    query = trigger.group(2).strip()
    
    logger.info(f'NVD CVE lookup: {query}')
    
    # Check if it's a CVE ID (CVE-YYYY-NNNN) or a search term
    if query.upper().startswith('CVE-'):
        # Direct CVE lookup
        cve_id = query.upper()
        url = f'https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={http.quote(cve_id)}'
    elif query.lower().startswith('search '):
        # Keyword search
        keyword = query[7:].strip()  # Remove "search " prefix
        url = f'https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={http.quote(keyword)}&resultsPerPage=3'
    else:
        # Assume it's a keyword search
        url = f'https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={http.quote(query)}&resultsPerPage=3'
    
    logger.debug(f'Querying NVD: {url}')
    data = http.get(url)
    
    if not data or 'vulnerabilities' not in data:
        bot.notice(trigger.nick, 'Failed to query NVD database.')
        return
    
    vulnerabilities = data.get('vulnerabilities', [])
    total = data.get('totalResults', len(vulnerabilities))
    
    if not vulnerabilities:
        bot.notice(trigger.nick, f'No CVEs found for "{query}".')
        return
    
    bot.say(f'NVD - Found {total:,} CVE(s) (showing {len(vulnerabilities)}):')
    
    for vuln in vulnerabilities[:3]:
        cve = vuln.get('cve', {})
        cve_id = cve.get('id', 'Unknown')
        descriptions = cve.get('descriptions', [])
        description = descriptions[0].get('value', 'Unknown') if descriptions else 'Unknown'
        
        # Get CVSS score if available
        metrics = cve.get('metrics', {})
        cvss_score = None
        cvss_severity = None
        if 'cvssMetricV31' in metrics:
            cvss_data = metrics['cvssMetricV31'][0].get('cvssData', {})
            cvss_score = cvss_data.get('baseScore')
            cvss_severity = cvss_data.get('baseSeverity')
        elif 'cvssMetricV30' in metrics:
            cvss_data = metrics['cvssMetricV30'][0].get('cvssData', {})
            cvss_score = cvss_data.get('baseScore')
            cvss_severity = cvss_data.get('baseSeverity')
        elif 'cvssMetricV2' in metrics:
            cvss_data = metrics['cvssMetricV2'][0].get('cvssData', {})
            cvss_score = cvss_data.get('baseScore')
        
        response = f"{formatter.bold(cve_id)}"
        if cvss_score is not None:
            response += f" | CVSS: {formatter.monospace(str(cvss_score))}"
            if cvss_severity:
                response += f" ({formatter.italic(cvss_severity)})"
        bot.say(formatter.truncate(response, max_len=400))
        
        desc_short = description[:150] + '...' if len(description) > 150 else description
        bot.say(f"  {formatter.italic(desc_short)}")




