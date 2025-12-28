"""
Sopel module for BGP APIs.
Supports BGPView API for IP, ASN, and prefix lookups.
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
        'name': 'BGPView',
        'description': 'IP, ASN, and prefix lookups for BGP routing information',
        'link': 'https://bgpview.docs.apiary.io',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('bgp')
@plugin.command('bgpview')
@plugin.example(f'.bgp')
def bgp_list(bot, trigger):
    """List all available BGP APIs."""
    bot.say(f'Available BGP APIs (1):')
    for i, api in enumerate(APIS[:10], 1):
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")


@plugin.command('bgp_info')
@plugin.example(f'.bgp_info <name>')
def bgp_info(bot, trigger):
    """Get information about a specific BGP API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .bgp_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('bgp_search')
@plugin.example(f'.bgp_search <query>')
def bgp_search(bot, trigger):
    """Search BGP APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .bgp_search <query>')
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
    for api in results[:5]:
        bot.say(f"- {api['name']}: {api['description'][:60]}")
    if len(results) > 5:
        bot.say(f'... and {len(results) - 5} more results')


@plugin.command('bgp_ip')
@plugin.example('.bgp_ip 8.8.8.8')
@plugin.example('.bgp_ip 2001:4860:4860::8888')
def bgp_ip(bot, trigger):
    """Get BGP information for an IP address using BGPView API."""
    # BGPView: https://bgpview.docs.apiary.io
    # Endpoint: GET https://api.bgpview.io/ip/{ip_address}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .bgp_ip <ip_address>')
        bot.notice(trigger.nick, 'Examples: .bgp_ip 8.8.8.8')
        bot.notice(trigger.nick, '          .bgp_ip 2001:4860:4860::8888')
        return
    
    ip_address = trigger.group(2).strip()
    
    logger.info(f'BGPView IP lookup: {ip_address}')
    
    encoded_ip = http.quote(ip_address)
    url = f'https://api.bgpview.io/ip/{encoded_ip}'
    
    logger.debug(f'Querying BGPView IP: {url}')
    data = http.get(url)
    
    if not data or 'status' not in data:
        bot.notice(trigger.nick, 'Failed to query BGPView API.')
        return
    
    if data.get('status') != 'ok':
        error_msg = data.get('status_message', 'Unknown error')
        bot.notice(trigger.nick, f'BGPView API error: {error_msg}')
        return
    
    data_payload = data.get('data', {})
    
    # IP information
    ip_addr = data_payload.get('ip', ip_address)
    ptr_record = data_payload.get('ptr_record', '')
    rir_allocation = data_payload.get('rir_allocation', {})
    rir_name = rir_allocation.get('rir_name', 'Unknown')
    
    # Prefixes (IPv4 and IPv6)
    prefixes = data_payload.get('prefixes', {})
    ipv4_prefixes = prefixes.get('ipv4', [])
    ipv6_prefixes = prefixes.get('ipv6', [])
    
    response = f"{formatter.bold('BGPView IP')}: {formatter.monospace(ip_addr)}"
    if rir_name:
        response += f" | RIR: {formatter.italic(rir_name)}"
    if ptr_record:
        response += f" | PTR: {formatter.monospace(ptr_record)}"
    bot.say(formatter.truncate(response, max_len=400))
    
    # Show prefixes
    if ipv4_prefixes:
        prefix_info = ipv4_prefixes[0]
        prefix = prefix_info.get('prefix', '')
        asn = prefix_info.get('asn', {})
        asn_num = asn.get('asn', '')
        asn_name = asn.get('name', '')
        
        prefix_line = f"IPv4: {formatter.bold(prefix)}"
        if asn_num:
            prefix_line += f" | AS{formatter.monospace(str(asn_num))}"
        if asn_name:
            prefix_line += f" ({formatter.italic(asn_name)})"
        bot.say(formatter.truncate(prefix_line, max_len=400))
    
    if ipv6_prefixes:
        prefix_info = ipv6_prefixes[0]
        prefix = prefix_info.get('prefix', '')
        asn = prefix_info.get('asn', {})
        asn_num = asn.get('asn', '')
        asn_name = asn.get('name', '')
        
        prefix_line = f"IPv6: {formatter.bold(prefix)}"
        if asn_num:
            prefix_line += f" | AS{formatter.monospace(str(asn_num))}"
        if asn_name:
            prefix_line += f" ({formatter.italic(asn_name)})"
        bot.say(formatter.truncate(prefix_line, max_len=400))


@plugin.command('bgp_asn')
@plugin.example('.bgp_asn 15169')
@plugin.example('.bgp_asn AS15169')
def bgp_asn(bot, trigger):
    """Get BGP information for an ASN using BGPView API."""
    # BGPView: https://bgpview.docs.apiary.io
    # Endpoint: GET https://api.bgpview.io/asn/{asn}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .bgp_asn <ASN>')
        bot.notice(trigger.nick, 'Examples: .bgp_asn 15169')
        bot.notice(trigger.nick, '          .bgp_asn AS15169')
        return
    
    asn_input = trigger.group(2).strip().upper()
    
    # Remove "AS" prefix if present
    if asn_input.startswith('AS'):
        asn_input = asn_input[2:]
    
    if not asn_input.isdigit():
        bot.notice(trigger.nick, 'ASN must be a number.')
        return
    
    logger.info(f'BGPView ASN lookup: {asn_input}')
    
    url = f'https://api.bgpview.io/asn/{asn_input}'
    
    logger.debug(f'Querying BGPView ASN: {url}')
    data = http.get(url)
    
    if not data or 'status' not in data:
        bot.notice(trigger.nick, 'Failed to query BGPView API.')
        return
    
    if data.get('status') != 'ok':
        error_msg = data.get('status_message', 'Unknown error')
        bot.notice(trigger.nick, f'BGPView API error: {error_msg}')
        return
    
    asn_data = data.get('data', {})
    
    asn_num = asn_data.get('asn', asn_input)
    name = asn_data.get('name', 'Unknown')
    description_short = asn_data.get('description_short', '')
    description_full = asn_data.get('description_full', [])
    country_code = asn_data.get('country_code', '')
    website = asn_data.get('website', '')
    
    # RIR information
    rir_allocation = asn_data.get('rir_allocation', {})
    rir_name = rir_allocation.get('rir_name', '')
    date_allocated = rir_allocation.get('date_allocated', '')
    
    # Prefixes
    ipv4_prefixes = asn_data.get('ipv4_prefixes', [])
    ipv6_prefixes = asn_data.get('ipv6_prefixes', [])
    
    response = f"{formatter.bold('AS' + str(asn_num))}: {formatter.bold(name)}"
    if country_code:
        response += f" | {formatter.italic(country_code)}"
    if rir_name:
        response += f" | RIR: {formatter.monospace(rir_name)}"
    bot.say(formatter.truncate(response, max_len=400))
    
    if description_short:
        bot.say(f"  {formatter.italic(description_short)}")
    
    if website:
        bot.say(f"  Website: {formatter.monospace(website)}")
    
    if ipv4_prefixes:
        bot.say(f"  IPv4 Prefixes: {formatter.monospace(str(len(ipv4_prefixes)))}")
    if ipv6_prefixes:
        bot.say(f"  IPv6 Prefixes: {formatter.monospace(str(len(ipv6_prefixes)))}")


@plugin.command('bgp_prefix')
@plugin.example('.bgp_prefix 8.8.8.0/24')
@plugin.example('.bgp_prefix 2001:4860::/32')
def bgp_prefix(bot, trigger):
    """Get BGP information for an IP prefix using BGPView API."""
    # BGPView: https://bgpview.docs.apiary.io
    # Endpoint: GET https://api.bgpview.io/prefix/{prefix}/{cidr}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .bgp_prefix <prefix>/<cidr>')
        bot.notice(trigger.nick, 'Examples: .bgp_prefix 8.8.8.0/24')
        bot.notice(trigger.nick, '          .bgp_prefix 2001:4860::/32')
        return
    
    prefix_input = trigger.group(2).strip()
    
    if '/' not in prefix_input:
        bot.notice(trigger.nick, 'Prefix must include CIDR notation (e.g., 8.8.8.0/24)')
        return
    
    logger.info(f'BGPView prefix lookup: {prefix_input}')
    
    encoded_prefix = http.quote(prefix_input)
    url = f'https://api.bgpview.io/prefix/{encoded_prefix}'
    
    logger.debug(f'Querying BGPView prefix: {url}')
    data = http.get(url)
    
    if not data or 'status' not in data:
        bot.notice(trigger.nick, 'Failed to query BGPView API.')
        return
    
    if data.get('status') != 'ok':
        error_msg = data.get('status_message', 'Unknown error')
        bot.notice(trigger.nick, f'BGPView API error: {error_msg}')
        return
    
    prefix_data = data.get('data', {})
    
    prefix = prefix_data.get('prefix', prefix_input)
    ip = prefix_data.get('ip', '')
    cidr = prefix_data.get('cidr', '')
    rir_name = prefix_data.get('rir_name', '')
    country_code = prefix_data.get('country_code', '')
    
    # ASN information
    asns = prefix_data.get('asns', [])
    
    response = f"{formatter.bold('BGPView Prefix')}: {formatter.monospace(prefix)}"
    if rir_name:
        response += f" | RIR: {formatter.italic(rir_name)}"
    if country_code:
        response += f" | Country: {formatter.monospace(country_code)}"
    bot.say(formatter.truncate(response, max_len=400))
    
    if asns:
        for asn_info in asns[:3]:  # Show first 3 ASNs
            asn_num = asn_info.get('asn', {})
            asn_id = asn_num.get('asn', '') if isinstance(asn_num, dict) else asn_num
            asn_name = asn_info.get('name', '')
            name = asn_num.get('name', '') if isinstance(asn_num, dict) and 'name' in asn_num else asn_name
            
            asn_line = f"  AS{formatter.monospace(str(asn_id))}"
            if name:
                asn_line += f": {formatter.italic(name)}"
            bot.say(formatter.truncate(asn_line, max_len=400))


@plugin.command('bgp_search_term')
@plugin.example('.bgp_search_term google')
@plugin.example('.bgp_search_term cloudflare')
def bgp_search_term(bot, trigger):
    """Search for ASNs by name or description using BGPView API."""
    # BGPView: https://bgpview.docs.apiary.io
    # Endpoint: GET https://api.bgpview.io/search?query_term={query}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .bgp_search_term <query>')
        bot.notice(trigger.nick, 'Examples: .bgp_search_term google')
        bot.notice(trigger.nick, '          .bgp_search_term cloudflare')
        return
    
    query = trigger.group(2).strip()
    
    logger.info(f'BGPView search: {query}')
    
    encoded_query = http.quote(query)
    url = f'https://api.bgpview.io/search?query_term={encoded_query}'
    
    logger.debug(f'Searching BGPView: {url}')
    data = http.get(url)
    
    if not data or 'status' not in data:
        bot.notice(trigger.nick, 'Failed to search BGPView API.')
        return
    
    if data.get('status') != 'ok':
        error_msg = data.get('status_message', 'Unknown error')
        bot.notice(trigger.nick, f'BGPView API error: {error_msg}')
        return
    
    search_data = data.get('data', {})
    ipv4_prefixes = search_data.get('ipv4_prefixes', [])
    ipv6_prefixes = search_data.get('ipv6_prefixes', [])
    asns = search_data.get('asns', [])
    
    total_results = len(ipv4_prefixes) + len(ipv6_prefixes) + len(asns)
    
    if total_results == 0:
        bot.notice(trigger.nick, f'No results found for "{query}".')
        return
    
    bot.say(f'BGPView Search - Found {total_results} result(s) for "{query}":')
    
    # Show ASNs
    if asns:
        bot.say(f"ASNs ({len(asns)}):")
        for asn in asns[:3]:
            asn_num = asn.get('asn', '')
            name = asn.get('name', 'Unknown')
            country_code = asn.get('country_code', '')
            
            asn_line = f"  AS{formatter.monospace(str(asn_num))}: {formatter.bold(name)}"
            if country_code:
                asn_line += f" ({formatter.italic(country_code)})"
            bot.say(formatter.truncate(asn_line, max_len=400))
    
    # Show IPv4 prefixes
    if ipv4_prefixes:
        bot.say(f"IPv4 Prefixes ({len(ipv4_prefixes)}):")
        for prefix_info in ipv4_prefixes[:2]:
            prefix = prefix_info.get('prefix', '')
            asn = prefix_info.get('asn', {})
            asn_num = asn.get('asn', '') if isinstance(asn, dict) else asn
            
            prefix_line = f"  {formatter.bold(prefix)}"
            if asn_num:
                prefix_line += f" | AS{formatter.monospace(str(asn_num))}"
            bot.say(formatter.truncate(prefix_line, max_len=400))
    
    # Show IPv6 prefixes
    if ipv6_prefixes:
        bot.say(f"IPv6 Prefixes ({len(ipv6_prefixes)}):")
        for prefix_info in ipv6_prefixes[:2]:
            prefix = prefix_info.get('prefix', '')
            asn = prefix_info.get('asn', {})
            asn_num = asn.get('asn', '') if isinstance(asn, dict) else asn
            
            prefix_line = f"  {formatter.bold(prefix)}"
            if asn_num:
                prefix_line += f" | AS{formatter.monospace(str(asn_num))}"
            bot.say(formatter.truncate(prefix_line, max_len=400))


@plugin.command('bgp_asn_prefixes')
@plugin.example('.bgp_asn_prefixes 15169')
@plugin.example('.bgp_asn_prefixes AS15169 ipv4')
def bgp_asn_prefixes(bot, trigger):
    """Get IP prefixes announced by an ASN using BGPView API."""
    # BGPView: https://bgpview.docs.apiary.io
    # Endpoint: GET https://api.bgpview.io/asn/{asn}/prefixes
    # Optional: ?ip_version=4 or ?ip_version=6
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .bgp_asn_prefixes <ASN> [ipv4|ipv6]')
        bot.notice(trigger.nick, 'Examples: .bgp_asn_prefixes 15169')
        bot.notice(trigger.nick, '          .bgp_asn_prefixes AS15169 ipv4')
        return
    
    parts = trigger.group(2).strip().split()
    asn_input = parts[0].upper()
    ip_version = parts[1].lower() if len(parts) > 1 else None
    
    # Remove "AS" prefix if present
    if asn_input.startswith('AS'):
        asn_input = asn_input[2:]
    
    if not asn_input.isdigit():
        bot.notice(trigger.nick, 'ASN must be a number.')
        return
    
    if ip_version and ip_version not in ['ipv4', 'ipv6', '4', '6']:
        bot.notice(trigger.nick, 'IP version must be ipv4, ipv6, 4, or 6.')
        return
    
    # Normalize IP version
    if ip_version in ['4', 'ipv4']:
        ip_version_param = '4'
    elif ip_version in ['6', 'ipv6']:
        ip_version_param = '6'
    else:
        ip_version_param = None
    
    logger.info(f'BGPView ASN prefixes lookup: {asn_input}, version: {ip_version_param}')
    
    url = f'https://api.bgpview.io/asn/{asn_input}/prefixes'
    if ip_version_param:
        url += f'?ip_version={ip_version_param}'
    
    logger.debug(f'Querying BGPView ASN prefixes: {url}')
    data = http.get(url)
    
    if not data or 'status' not in data:
        bot.notice(trigger.nick, 'Failed to query BGPView API.')
        return
    
    if data.get('status') != 'ok':
        error_msg = data.get('status_message', 'Unknown error')
        bot.notice(trigger.nick, f'BGPView API error: {error_msg}')
        return
    
    prefixes_data = data.get('data', {})
    ipv4_prefixes = prefixes_data.get('ipv4_prefixes', [])
    ipv6_prefixes = prefixes_data.get('ipv6_prefixes', [])
    
    total = len(ipv4_prefixes) + len(ipv6_prefixes)
    
    if total == 0:
        bot.notice(trigger.nick, f'No prefixes found for AS{asn_input}.')
        return
    
    response = f"{formatter.bold('AS' + str(asn_input))} Prefixes:"
    if ipv4_prefixes:
        response += f" {formatter.monospace(str(len(ipv4_prefixes)))} IPv4"
    if ipv6_prefixes:
        response += f" {formatter.monospace(str(len(ipv6_prefixes)))} IPv6"
    bot.say(response)
    
    # Show sample prefixes
    if ipv4_prefixes:
        bot.say(f"IPv4 (showing {min(3, len(ipv4_prefixes))}):")
        for prefix_info in ipv4_prefixes[:3]:
            prefix = prefix_info.get('prefix', '')
            name = prefix_info.get('name', '')
            
            prefix_line = f"  {formatter.bold(prefix)}"
            if name:
                prefix_line += f" | {formatter.italic(name)}"
            bot.say(formatter.truncate(prefix_line, max_len=400))
    
    if ipv6_prefixes:
        bot.say(f"IPv6 (showing {min(3, len(ipv6_prefixes))}):")
        for prefix_info in ipv6_prefixes[:3]:
            prefix = prefix_info.get('prefix', '')
            name = prefix_info.get('name', '')
            
            prefix_line = f"  {formatter.bold(prefix)}"
            if name:
                prefix_line += f" | {formatter.italic(name)}"
            bot.say(formatter.truncate(prefix_line, max_len=400))


@plugin.command('bgp_asn_peers')
@plugin.example('.bgp_asn_peers 15169')
def bgp_asn_peers(bot, trigger):
    """Get BGP peers (upstream/downstream) for an ASN using BGPView API."""
    # BGPView: https://bgpview.docs.apiary.io
    # Endpoint: GET https://api.bgpview.io/asn/{asn}/peers
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .bgp_asn_peers <ASN>')
        bot.notice(trigger.nick, 'Example: .bgp_asn_peers 15169')
        return
    
    asn_input = trigger.group(2).strip().upper()
    
    # Remove "AS" prefix if present
    if asn_input.startswith('AS'):
        asn_input = asn_input[2:]
    
    if not asn_input.isdigit():
        bot.notice(trigger.nick, 'ASN must be a number.')
        return
    
    logger.info(f'BGPView ASN peers lookup: {asn_input}')
    
    url = f'https://api.bgpview.io/asn/{asn_input}/peers'
    
    logger.debug(f'Querying BGPView ASN peers: {url}')
    data = http.get(url)
    
    if not data or 'status' not in data:
        bot.notice(trigger.nick, 'Failed to query BGPView API.')
        return
    
    if data.get('status') != 'ok':
        error_msg = data.get('status_message', 'Unknown error')
        bot.notice(trigger.nick, f'BGPView API error: {error_msg}')
        return
    
    peers_data = data.get('data', {})
    ipv4_peers = peers_data.get('ipv4_peers', [])
    ipv6_peers = peers_data.get('ipv6_peers', [])
    
    total = len(ipv4_peers) + len(ipv6_peers)
    
    if total == 0:
        bot.notice(trigger.nick, f'No peers found for AS{asn_input}.')
        return
    
    bot.say(f"{formatter.bold('AS' + str(asn_input))} Peers: {formatter.monospace(str(total))} total")
    
    # Show IPv4 peers
    if ipv4_peers:
        bot.say(f"IPv4 Peers ({len(ipv4_peers)}, showing {min(3, len(ipv4_peers))}):")
        for peer in ipv4_peers[:3]:
            asn = peer.get('asn', {})
            asn_num = asn.get('asn', '') if isinstance(asn, dict) else peer.get('asn', '')
            name = asn.get('name', '') if isinstance(asn, dict) else peer.get('name', 'Unknown')
            
            peer_line = f"  AS{formatter.monospace(str(asn_num))}: {formatter.italic(name)}"
            bot.say(formatter.truncate(peer_line, max_len=400))
    
    # Show IPv6 peers
    if ipv6_peers:
        bot.say(f"IPv6 Peers ({len(ipv6_peers)}, showing {min(3, len(ipv6_peers))}):")
        for peer in ipv6_peers[:3]:
            asn = peer.get('asn', {})
            asn_num = asn.get('asn', '') if isinstance(asn, dict) else peer.get('asn', '')
            name = asn.get('name', '') if isinstance(asn, dict) else peer.get('name', 'Unknown')
            
            peer_line = f"  AS{formatter.monospace(str(asn_num))}: {formatter.italic(name)}"
            bot.say(formatter.truncate(peer_line, max_len=400))


@plugin.command('bgp_asn_upstreams')
@plugin.example('.bgp_asn_upstreams 15169')
def bgp_asn_upstreams(bot, trigger):
    """Get BGP upstream ASNs for an ASN using BGPView API."""
    # BGPView: https://bgpview.docs.apiary.io
    # Endpoint: GET https://api.bgpview.io/asn/{asn}/upstreams
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .bgp_asn_upstreams <ASN>')
        bot.notice(trigger.nick, 'Example: .bgp_asn_upstreams 15169')
        return
    
    asn_input = trigger.group(2).strip().upper()
    
    # Remove "AS" prefix if present
    if asn_input.startswith('AS'):
        asn_input = asn_input[2:]
    
    if not asn_input.isdigit():
        bot.notice(trigger.nick, 'ASN must be a number.')
        return
    
    logger.info(f'BGPView ASN upstreams lookup: {asn_input}')
    
    url = f'https://api.bgpview.io/asn/{asn_input}/upstreams'
    
    logger.debug(f'Querying BGPView ASN upstreams: {url}')
    data = http.get(url)
    
    if not data or 'status' not in data:
        bot.notice(trigger.nick, 'Failed to query BGPView API.')
        return
    
    if data.get('status') != 'ok':
        error_msg = data.get('status_message', 'Unknown error')
        bot.notice(trigger.nick, f'BGPView API error: {error_msg}')
        return
    
    upstreams_data = data.get('data', {})
    ipv4_upstreams = upstreams_data.get('ipv4_upstreams', [])
    ipv6_upstreams = upstreams_data.get('ipv6_upstreams', [])
    
    total = len(ipv4_upstreams) + len(ipv6_upstreams)
    
    if total == 0:
        bot.notice(trigger.nick, f'No upstreams found for AS{asn_input}.')
        return
    
    bot.say(f"{formatter.bold('AS' + str(asn_input))} Upstreams: {formatter.monospace(str(total))} total")
    
    # Show IPv4 upstreams
    if ipv4_upstreams:
        bot.say(f"IPv4 Upstreams ({len(ipv4_upstreams)}, showing {min(3, len(ipv4_upstreams))}):")
        for upstream in ipv4_upstreams[:3]:
            asn = upstream.get('asn', {})
            asn_num = asn.get('asn', '') if isinstance(asn, dict) else upstream.get('asn', '')
            name = asn.get('name', '') if isinstance(asn, dict) else upstream.get('name', 'Unknown')
            
            upstream_line = f"  AS{formatter.monospace(str(asn_num))}: {formatter.italic(name)}"
            bot.say(formatter.truncate(upstream_line, max_len=400))
    
    # Show IPv6 upstreams
    if ipv6_upstreams:
        bot.say(f"IPv6 Upstreams ({len(ipv6_upstreams)}, showing {min(3, len(ipv6_upstreams))}):")
        for upstream in ipv6_upstreams[:3]:
            asn = upstream.get('asn', {})
            asn_num = asn.get('asn', '') if isinstance(asn, dict) else upstream.get('asn', '')
            name = asn.get('name', '') if isinstance(asn, dict) else upstream.get('name', 'Unknown')
            
            upstream_line = f"  AS{formatter.monospace(str(asn_num))}: {formatter.italic(name)}"
            bot.say(formatter.truncate(upstream_line, max_len=400))


@plugin.command('bgp_asn_downstreams')
@plugin.example('.bgp_asn_downstreams 15169')
def bgp_asn_downstreams(bot, trigger):
    """Get BGP downstream ASNs for an ASN using BGPView API."""
    # BGPView: https://bgpview.docs.apiary.io
    # Endpoint: GET https://api.bgpview.io/asn/{asn}/downstreams
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .bgp_asn_downstreams <ASN>')
        bot.notice(trigger.nick, 'Example: .bgp_asn_downstreams 15169')
        return
    
    asn_input = trigger.group(2).strip().upper()
    
    # Remove "AS" prefix if present
    if asn_input.startswith('AS'):
        asn_input = asn_input[2:]
    
    if not asn_input.isdigit():
        bot.notice(trigger.nick, 'ASN must be a number.')
        return
    
    logger.info(f'BGPView ASN downstreams lookup: {asn_input}')
    
    url = f'https://api.bgpview.io/asn/{asn_input}/downstreams'
    
    logger.debug(f'Querying BGPView ASN downstreams: {url}')
    data = http.get(url)
    
    if not data or 'status' not in data:
        bot.notice(trigger.nick, 'Failed to query BGPView API.')
        return
    
    if data.get('status') != 'ok':
        error_msg = data.get('status_message', 'Unknown error')
        bot.notice(trigger.nick, f'BGPView API error: {error_msg}')
        return
    
    downstreams_data = data.get('data', {})
    ipv4_downstreams = downstreams_data.get('ipv4_downstreams', [])
    ipv6_downstreams = downstreams_data.get('ipv6_downstreams', [])
    
    total = len(ipv4_downstreams) + len(ipv6_downstreams)
    
    if total == 0:
        bot.notice(trigger.nick, f'No downstreams found for AS{asn_input}.')
        return
    
    bot.say(f"{formatter.bold('AS' + str(asn_input))} Downstreams: {formatter.monospace(str(total))} total")
    
    # Show IPv4 downstreams
    if ipv4_downstreams:
        bot.say(f"IPv4 Downstreams ({len(ipv4_downstreams)}, showing {min(3, len(ipv4_downstreams))}):")
        for downstream in ipv4_downstreams[:3]:
            asn = downstream.get('asn', {})
            asn_num = asn.get('asn', '') if isinstance(asn, dict) else downstream.get('asn', '')
            name = asn.get('name', '') if isinstance(asn, dict) else downstream.get('name', 'Unknown')
            
            downstream_line = f"  AS{formatter.monospace(str(asn_num))}: {formatter.italic(name)}"
            bot.say(formatter.truncate(downstream_line, max_len=400))
    
    # Show IPv6 downstreams
    if ipv6_downstreams:
        bot.say(f"IPv6 Downstreams ({len(ipv6_downstreams)}, showing {min(3, len(ipv6_downstreams))}):")
        for downstream in ipv6_downstreams[:3]:
            asn = downstream.get('asn', {})
            asn_num = asn.get('asn', '') if isinstance(asn, dict) else downstream.get('asn', '')
            name = asn.get('name', '') if isinstance(asn, dict) else downstream.get('name', 'Unknown')
            
            downstream_line = f"  AS{formatter.monospace(str(asn_num))}: {formatter.italic(name)}"
            bot.say(formatter.truncate(downstream_line, max_len=400))


def setup(bot):
    """Module setup - BGP APIs loaded."""
    bot.memory['bgp_loaded'] = True
    bot.memory['bgp_count'] = 1
    logger.info('BGP module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['bgp_loaded'] = False
    logger.info('BGP module unloaded')

