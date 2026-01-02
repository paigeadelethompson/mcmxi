"""
Sopel module for DNS queries and operations.
Supports multiple DNS record types, DNS over HTTPS (DoH), and anycast
resolvers.
"""

import ipaddress
import os
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from sopel import plugin

# Import utilities - avoid circular imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from irc_formatter import IRCFormatter
from sopel.tools import get_logger


def get_module_logger(name: str):
    """Get a logger for a module."""
    return get_logger(name)

logger = get_module_logger(__name__)
formatter = IRCFormatter()

# DNS Record Types
RECORD_TYPES = {
    'A': 1,
    'AAAA': 28,
    'CNAME': 5,
    'MX': 15,
    'TXT': 16,
    'NS': 2,
    'SOA': 6,
    'PTR': 12,
    'SRV': 33,
    'CAA': 257,
    'DNSKEY': 48,
    'DS': 43,
    'NAPTR': 35,
    'TLSA': 52,
    'SSHFP': 44,
    'CERT': 37,
    'OPENPGPKEY': 61,
    'HTTPS': 65,
    'SVCB': 64,
    'URI': 256,
    'SPF': 99,
}

# DoH (DNS over HTTPS) Providers
DOH_PROVIDERS = {
    'cloudflare': {
        'url': 'https://1.1.1.1/dns-query',
        'name': 'Cloudflare',
    },
    'cloudflare_malware': {
        'url': 'https://security.cloudflare-dns.com/dns-query',
        'name': 'Cloudflare (Malware Blocking)',
    },
    'cloudflare_adult': {
        'url': 'https://family.cloudflare-dns.com/dns-query',
        'name': 'Cloudflare (Adult Content Blocking)',
    },
    'google': {
        'url': 'https://8.8.8.8/resolve',
        'name': 'Google',
    },
    'google_ipv6': {
        'url': 'https://[2001:4860:4860::8888]/resolve',
        'name': 'Google (IPv6)',
    },
    'quad9': {
        'url': 'https://9.9.9.9/dns-query',
        'name': 'Quad9',
    },
    'quad9_ipv6': {
        'url': 'https://[2620:fe::fe]/dns-query',
        'name': 'Quad9 (IPv6)',
    },
    'opendns': {
        'url': 'https://doh.opendns.com/dns-query',
        'name': 'OpenDNS',
    },
    'adguard': {
        'url': 'https://dns.adguard.com/dns-query',
        'name': 'AdGuard',
    },
    'adguard_family': {
        'url': 'https://dns-family.adguard.com/dns-query',
        'name': 'AdGuard (Family)',
    },
    'nextdns': {
        'url': 'https://dns.nextdns.io/dns-query',
        'name': 'NextDNS',
    },
    'cleanbrowsing': {
        'url': 'https://doh.cleanbrowsing.org/doh/security-filter/',
        'name': 'CleanBrowsing (Security)',
    },
    'cleanbrowsing_family': {
        'url': 'https://doh.cleanbrowsing.org/doh/family-filter/',
        'name': 'CleanBrowsing (Family)',
    },
    'controld': {
        'url': 'https://freedns.controld.com/dns-query',
        'name': 'Control D',
    },
}


def _is_ipv6_available() -> bool:
    """Check if IPv6 is actually reachable on the system."""
    try:
        import socket
        # Try to connect to a known IPv6 address to test actual reachability
        test_sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        test_sock.settimeout(1.0)
        try:
            # Try to connect to Google's IPv6 DNS
            test_sock.connect(('2001:4860:4860::8888', 53))
            test_sock.close()
            return True
        except (socket.error, OSError, TimeoutError):
            test_sock.close()
            return False
    except Exception:
        return False


def query_doh(domain: str, record_type: str,
              provider_url: str) -> Optional[Dict[str, Any]]:
    """Query DNS over HTTPS using requests library."""
    try:
        rtype = RECORD_TYPES.get(record_type.upper())
        if rtype is None:
            return None

        # Get proxy from environment
        proxies = {}
        https_proxy = (os.environ.get('HTTPS_PROXY') or
                       os.environ.get('HTTP_PROXY'))
        http_proxy = os.environ.get('HTTP_PROXY')
        if https_proxy:
            proxies['https'] = https_proxy
        if http_proxy:
            proxies['http'] = http_proxy

        # Prepare DoH query
        params = {
            'name': domain,
            'type': record_type.upper(),
        }

        headers = {
            'Accept': 'application/dns-json',
        }

        # Make request with timeout
        response = requests.get(
            provider_url,
            params=params,
            headers=headers,
            proxies=proxies if proxies else None,
            timeout=5.0,
            verify=True
        )

        if response.status_code != 200:
            return None

        data = response.json()

        # Check if query was successful
        if data.get('Status') != 0:
            return None

        # Return the response data
        return data
    except Exception as e:
        logger.debug(
            f'DoH query failed for {domain} ({record_type}) '
            f'via {provider_url}: {e}'
        )
        return None


class AnycastDoHResolver:
    """Anycast DNS over HTTPS resolver that queries providers in parallel."""

    def __init__(self, providers: Optional[List[str]] = None):
        if providers is None:
            providers = list(DOH_PROVIDERS.keys())
        
        # Filter out IPv6 providers if IPv6 is not available
        ipv6_available = _is_ipv6_available()
        if not ipv6_available:
            # Remove providers that use IPv6 addresses
            ipv6_providers = ['google_ipv6', 'quad9_ipv6']
            providers = [p for p in providers if p not in ipv6_providers]
        
        self.providers = [DOH_PROVIDERS[p] for p in providers if p in DOH_PROVIDERS]
        self.logger = get_module_logger('anycast_doh')

    def query(self, domain: str,
              record_type: str = 'A') -> Optional[Dict[str, Any]]:
        """Perform DNS query using multithreaded anycast."""
        if not self.providers:
            self.logger.warning('No providers available for DNS query')
            return None

        self.logger.info(
            f'Querying {domain} ({record_type}) using '
            f'{len(self.providers)} DoH providers'
        )
        result_container = {'response': None, 'lock': threading.Lock()}
        result_event = threading.Event()

        def query_provider(provider: Dict[str, Any]):
            if result_event.is_set():
                return
            try:
                self.logger.debug(
                    f'Trying provider {provider["name"]} '
                    f'({provider["url"]}) for {domain}'
                )
                response = query_doh(domain, record_type, provider['url'])
                if response and response.get('Answer'):
                    with result_container['lock']:
                        if result_container['response'] is None:
                            result_container['response'] = response
                            self.logger.info(
                                f'Provider {provider["name"]} resolved '
                                f'{domain} ({record_type})'
                            )
                            result_event.set()
            except Exception as e:
                self.logger.debug(
                    f'Provider {provider["name"]} failed for {domain}: {e}'
                )

        threads = []
        for provider in self.providers:
            thread = threading.Thread(target=query_provider, args=(provider,), daemon=True)
            thread.start()
            threads.append(thread)

        result_event.wait(timeout=5.0)

        for thread in threads:
            thread.join(timeout=0.1)

        if result_container['response'] is None:
            self.logger.warning(
                f'All providers failed to resolve {domain} ({record_type})'
            )
        return result_container['response']


# Global resolver
anycast_resolver = AnycastDoHResolver()


def resolve_hostname_dot(hostname: str) -> Optional[str]:
    """Resolve hostname to IP using DoH.

    Returns IPv4, or IPv6 only if IPv6 is available.
    """
    logger.info(f'Resolving {hostname} using DoH')
    start_time = time.time()

    ipv6_available = _is_ipv6_available()
    logger.info(f'IPv6 available: {ipv6_available}')

    # Try AAAA (IPv6) only if IPv6 is available
    if ipv6_available:
        logger.info(f'Querying AAAA record for {hostname}')
        response = anycast_resolver.query(hostname, 'AAAA')
        if response and response.get('Answer'):
            for answer in response['Answer']:
                if answer.get('type') == 28:  # AAAA record
                    ip = answer.get('data')
                    if ip:
                        elapsed = time.time() - start_time
                        logger.info(
                            f'Resolved {hostname} to IPv6 {ip} '
                            f'in {elapsed:.2f}s'
                        )
                        return ip

    # Use A (IPv4) - primary method
    logger.info(f'Querying A record for {hostname}')
    response = anycast_resolver.query(hostname, 'A')
    if response and response.get('Answer'):
        for answer in response['Answer']:
            if answer.get('type') == 1:  # A record
                ip = answer.get('data')
                if ip:
                    elapsed = time.time() - start_time
                    logger.info(
                        f'Resolved {hostname} to IPv4 {ip} '
                        f'in {elapsed:.2f}s'
                    )
                    return ip

    elapsed = time.time() - start_time
    logger.warning(
        f'Failed to resolve {hostname} using DoH after {elapsed:.2f}s'
    )
    return None


def query_standard(domain: str, record_type: str,
                   nameserver: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Query DNS using standard resolver (fallback to DoH)."""
    try:
        # Use DoH as standard resolver
        response = anycast_resolver.query(domain, record_type)
        return response
    except Exception:
        return None


def format_dns_response(answers: Any, record_type: str) -> str:
    """Format DNS response for IRC output."""
    if not answers:
        return 'No records found'

    results = []
    record_type_upper = record_type.upper()
    rtype_num = RECORD_TYPES.get(record_type_upper, 0)

    try:
        # Handle DoH JSON response
        if isinstance(answers, dict):
            answer_list = answers.get('Answer', [])
            for answer in answer_list:
                if answer.get('type') == rtype_num:
                    data = answer.get('data', '')
                    if record_type_upper == 'MX':
                        # MX format: priority exchange
                        parts = data.split(' ', 1)
                        if len(parts) == 2:
                            results.append(f"{parts[0]} {parts[1]}")
                        else:
                            results.append(data)
                    elif record_type_upper == 'TXT':
                        # Remove quotes from TXT records
                        results.append(data.strip('"'))
                    elif record_type_upper == 'SRV':
                        # SRV format: priority weight port target
                        results.append(data)
                    else:
                        results.append(data)
        # Handle legacy format (for compatibility)
        elif hasattr(answers, 'answer'):
            for rrset in answers.answer:
                for rdata in rrset:
                    results.append(
                        format_rdata(rdata, record_type_upper)
                    )
        else:
            for rdata in answers:
                results.append(format_rdata(rdata, record_type_upper))
    except Exception as e:
        return f'Error formatting response: {e}'

    if not results:
        return 'No records found'

    return ' | '.join(results[:5])


def format_rdata(rdata: Any, record_type: str) -> str:
    """Format a single DNS record (legacy format support)."""
    try:
        if record_type in ('A', 'AAAA'):
            return str(rdata.address)
        elif record_type == 'CNAME':
            return str(rdata.target)
        elif record_type == 'MX':
            return f"{rdata.preference} {rdata.exchange}"
        elif record_type == 'TXT':
            txt_strings = [
                s.decode('utf-8', errors='replace')
                if isinstance(s, bytes) else str(s)
                for s in rdata.strings
            ]
            return ' '.join(txt_strings)
        elif record_type == 'NS':
            return str(rdata.target)
        elif record_type == 'SOA':
            return f"{rdata.mname} {rdata.rname} {rdata.serial}"
        elif record_type == 'PTR':
            return str(rdata.target)
        elif record_type == 'SRV':
            return f"{rdata.priority} {rdata.weight} {rdata.port} {rdata.target}"
        else:
            return str(rdata)
    except Exception:
        return str(rdata)


@plugin.command('dns')
@plugin.example('`dns example.com')
def dns_query(bot, trigger):
    """Query DNS records. Usage: `dns <domain> [record_type]"""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `dns <domain> [record_type]')
        return

    args = trigger.group(2).strip().split()
    domain = args[0]
    record_type = args[1].upper() if len(args) > 1 else 'A'

    if record_type not in RECORD_TYPES:
        bot.notice(trigger.nick, f'Unsupported record type: {record_type}')
        return

    try:
        answers = query_standard(domain, record_type)
        if not answers:
            bot.notice(trigger.nick, f'No {record_type} records found for {domain}')
            return

        formatted = format_dns_response(answers, record_type)
        bot.say(f"{formatter.bold(domain)} {record_type}: {formatted}")
    except Exception as e:
        logger.exception('DNS query error', e)
        bot.notice(trigger.nick, f'DNS query failed: {e}')


@plugin.command('dns_doh')
@plugin.example('`dns_doh example.com A')
def dns_doh(bot, trigger):
    """Query DNS over HTTPS. Usage: `dns_doh <domain> [record_type]"""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `dns_doh <domain> [record_type]')
        return

    args = trigger.group(2).strip().split()
    domain = args[0]
    record_type = args[1].upper() if len(args) > 1 else 'A'

    if record_type not in RECORD_TYPES:
        bot.notice(trigger.nick, f'Unsupported record type: {record_type}')
        return

    try:
        response = anycast_resolver.query(domain, record_type)
        if not response:
            bot.notice(
                trigger.nick,
                f'No {record_type} records found for {domain}'
            )
            return

        formatted = format_dns_response(response, record_type)
        bot.say(
            f"{formatter.bold(domain)} {record_type} (DoH): {formatted}"
        )
    except Exception as e:
        logger.exception('DoH query error', e)
        bot.notice(trigger.nick, f'DoH query failed: {e}')


def setup(bot):
    """Module setup."""
    bot.memory['dns_loaded'] = True
    logger.info('DNS module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['dns_loaded'] = False
    logger.info('DNS module unloaded')
