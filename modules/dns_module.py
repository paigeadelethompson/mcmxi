"""
Sopel module for DNS queries and operations.
Supports multiple DNS record types, DNS over TLS (DoT), XFR over TLS (XoT),
and round-robin/anycast DoTLS resolvers.
"""

from sopel import plugin
import sys
import os
import time
import itertools
import threading
from typing import Optional, Dict, List, Any, Tuple
from urllib.parse import urlparse
# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get_module_logger, IRCFormatter

logger = get_module_logger(__name__)
formatter = IRCFormatter()

# Import dnspython
import dns.resolver
import dns.query
import dns.message
import dns.rdatatype
import dns.rdataclass
import dns.zone
import dns.exception
import dns.name
import ssl


# DNS Record Types
RECORD_TYPES = {
    'A': dns.rdatatype.A,
    'AAAA': dns.rdatatype.AAAA,
    'CNAME': dns.rdatatype.CNAME,
    'MX': dns.rdatatype.MX,
    'TXT': dns.rdatatype.TXT,
    'NS': dns.rdatatype.NS,
    'SOA': dns.rdatatype.SOA,
    'PTR': dns.rdatatype.PTR,
    'SRV': dns.rdatatype.SRV,
    'CAA': dns.rdatatype.CAA,
    'DNSKEY': dns.rdatatype.DNSKEY,
    'DS': dns.rdatatype.DS,
    'NAPTR': dns.rdatatype.NAPTR,
    'TLSA': dns.rdatatype.TLSA,
    'SSHFP': dns.rdatatype.SSHFP,
    'CERT': dns.rdatatype.CERT,
    'OPENPGPKEY': dns.rdatatype.OPENPGPKEY,
    'HTTPS': dns.rdatatype.HTTPS,
    'SVCB': dns.rdatatype.SVCB,
    'URI': dns.rdatatype.URI,
    'SPF': dns.rdatatype.SPF,
    'AXFR': dns.rdatatype.AXFR,
    'IXFR': dns.rdatatype.IXFR,
}


# DoT (DNS over TLS) Providers
DOT_PROVIDERS = {
    'cloudflare': {
        'hostname': '1dot1dot1dot1.cloudflare-dns.com',
        'ip': '1.1.1.1',
        'port': 853,
        'name': 'Cloudflare',
    },
    'cloudflare_malware': {
        'hostname': 'security.cloudflare-dns.com',
        'ip': '1.1.1.2',
        'port': 853,
        'name': 'Cloudflare (Malware Blocking)',
    },
    'cloudflare_adult': {
        'hostname': 'family.cloudflare-dns.com',
        'ip': '1.1.1.3',
        'port': 853,
        'name': 'Cloudflare (Adult Content Blocking)',
    },
    'google': {
        'hostname': 'dns.google',
        'ip': '8.8.8.8',
        'port': 853,
        'name': 'Google',
    },
    'google_ipv6': {
        'hostname': 'dns.google',
        'ip': '2001:4860:4860::8888',
        'port': 853,
        'name': 'Google (IPv6)',
    },
    'quad9': {
        'hostname': 'dns.quad9.net',
        'ip': '9.9.9.9',
        'port': 853,
        'name': 'Quad9',
    },
    'quad9_ipv6': {
        'hostname': 'dns.quad9.net',
        'ip': '2620:fe::fe',
        'port': 853,
        'name': 'Quad9 (IPv6)',
    },
    'opendns': {
        'hostname': 'dns.opendns.com',
        'ip': '208.67.222.222',
        'port': 853,
        'name': 'OpenDNS',
    },
    'opendns_family': {
        'hostname': 'dns.opendns.com',
        'ip': '208.67.222.123',
        'port': 853,
        'name': 'OpenDNS (FamilyShield)',
    },
    'adguard': {
        'hostname': 'dns.adguard.com',
        'ip': '94.140.14.14',
        'port': 853,
        'name': 'AdGuard',
    },
    'adguard_family': {
        'hostname': 'dns-family.adguard.com',
        'ip': '94.140.14.15',
        'port': 853,
        'name': 'AdGuard (Family)',
    },
    'nextdns': {
        'hostname': 'dns.nextdns.io',
        'ip': '45.90.28.0',
        'port': 853,
        'name': 'NextDNS',
    },
    'cleanbrowsing': {
        'hostname': 'security-filter-dns.cleanbrowsing.org',
        'ip': '185.228.168.9',
        'port': 853,
        'name': 'CleanBrowsing (Security)',
    },
    'cleanbrowsing_family': {
        'hostname': 'family-filter-dns.cleanbrowsing.org',
        'ip': '185.228.168.168',
        'port': 853,
        'name': 'CleanBrowsing (Family)',
    },
    'comodo': {
        'hostname': 'ns1.recursive.dnsbycomodo.com',
        'ip': '8.26.56.26',
        'port': 853,
        'name': 'Comodo Secure DNS',
    },
    'yandex': {
        'hostname': 'dns.yandex.ru',
        'ip': '77.88.8.8',
        'port': 853,
        'name': 'Yandex DNS',
    },
    'uncensoreddns': {
        'hostname': 'anycast.censurfridns.dk',
        'ip': '91.239.100.100',
        'port': 853,
        'name': 'UncensoredDNS',
    },
    'mullvad': {
        'hostname': 'doh.mullvad.net',
        'ip': '194.242.2.2',
        'port': 853,
        'name': 'Mullvad',
    },
    'controld': {
        'hostname': 'freedns.controld.com',
        'ip': '76.76.2.0',
        'port': 853,
        'name': 'Control D',
    },
}


# Round-robin DoTLS resolver
class RoundRobinDoTLSResolver:
    """Round-robin DNS over TLS resolver that cycles through providers."""
    
    def __init__(self, providers: Optional[List[str]] = None):
        """Initialize with list of provider keys, or use all providers."""
        if providers is None:
            providers = list(DOT_PROVIDERS.keys())
        
        self.providers = [DOT_PROVIDERS[p] for p in providers if p in DOT_PROVIDERS]
        self.iterator = itertools.cycle(self.providers)
        self.logger = get_module_logger('roundrobin_dotls')
    
    def get_next(self) -> Dict[str, Any]:
        """Get next provider in round-robin order."""
        return next(self.iterator)
    
    def query(self, domain: str, record_type: str = 'A') -> Tuple[Optional[Any], Dict[str, Any]]:
        """Perform DNS query using next provider in round-robin. Returns (response, provider)."""
        provider = self.get_next()
        response = query_dot(domain, record_type, provider['hostname'], provider['port'])
        return response, provider


# Anycast DoTLS resolver
class AnycastDoTLSResolver:
    """Anycast DNS over TLS resolver that queries all providers in parallel and returns first result."""
    
    def __init__(self, providers: Optional[List[str]] = None):
        """Initialize with list of provider keys, or use all providers."""
        if providers is None:
            providers = list(DOT_PROVIDERS.keys())
        
        self.providers = [DOT_PROVIDERS[p] for p in providers if p in DOT_PROVIDERS]
        self.logger = get_module_logger('anycast_dotls')
    
    def query(self, domain: str, record_type: str = 'A') -> Optional[Any]:
        """Perform DNS query using multithreaded anycast - queries all providers in parallel, returns first result."""
        if not self.providers:
            return None
        
        result_container = {'response': None, 'lock': threading.Lock()}
        threads = []
        
        def query_provider(provider: Dict[str, Any]):
            """Query a single provider and set result if successful."""
            try:
                response = query_dot(domain, record_type, provider['hostname'], provider['port'])
                if response:
                    with result_container['lock']:
                        if result_container['response'] is None:
                            result_container['response'] = response
            except Exception as e:
                self.logger.debug(f'Provider {provider["name"]} failed: {e}')
        
        # Start threads for all providers
        for provider in self.providers:
            thread = threading.Thread(target=query_provider, args=(provider,), daemon=True)
            thread.start()
            threads.append(thread)
        
        # Wait for first result or all threads to complete
        for thread in threads:
            thread.join(timeout=5.0)  # 5 second timeout per thread
            if result_container['response'] is not None:
                # Got a result, can return early (other threads are daemon so they'll finish on their own)
                break
        
        return result_container['response']


# Global resolvers
roundrobin_resolver = RoundRobinDoTLSResolver()
anycast_resolver = AnycastDoTLSResolver()


def query_dot(domain: str, record_type: str, hostname: str, port: int = 853) -> Optional[Any]:
    """Query DNS over TLS."""
    try:
        rtype = RECORD_TYPES.get(record_type.upper())
        if rtype is None:
            logger.error(f'Unsupported record type: {record_type}')
            return None
        
        query = dns.message.make_query(domain, rtype)
        response = dns.query.tls(query, hostname, port=port, timeout=5.0)
        
        return response
    except Exception as e:
        logger.exception(f'DoT query failed for {domain} ({record_type})', e)
        return None


def query_standard(domain: str, record_type: str, nameserver: Optional[str] = None) -> Optional[Any]:
    """Query DNS using standard resolver."""
    try:
        resolver = dns.resolver.Resolver()
        if nameserver:
            resolver.nameservers = [nameserver]
        
        rtype = RECORD_TYPES.get(record_type.upper())
        if rtype is None:
            logger.error(f'Unsupported record type: {record_type}')
            return None
        
        answers = resolver.resolve(domain, record_type.upper())
        return answers
    except Exception as e:
        logger.exception(f'DNS query failed for {domain} ({record_type})', e)
        return None


def format_dns_response(answers: Any, record_type: str) -> str:
    """Format DNS response for IRC output."""
    if not answers:
        return 'No records found'
    
    results = []
    record_type_upper = record_type.upper()
    
    try:
        if hasattr(answers, 'rrset'):
            # dns.resolver.Answer object
            for rdata in answers:
                results.append(format_rdata(rdata, record_type_upper))
        elif hasattr(answers, 'answer'):
            # dns.message.Message object
            for rrset in answers.answer:
                for rdata in rrset:
                    results.append(format_rdata(rdata, record_type_upper))
        else:
            # Direct rdata list
            for rdata in answers:
                results.append(format_rdata(rdata, record_type_upper))
    except Exception as e:
        logger.exception('Error formatting DNS response', e)
        return f'Error formatting response: {e}'
    
    if not results:
        return 'No records found'
    
    return ' | '.join(results[:5])  # Limit to 5 results


def format_rdata(rdata: Any, record_type: str) -> str:
    """Format a single DNS record."""
    try:
        if record_type == 'A':
            return str(rdata.address)
        elif record_type == 'AAAA':
            return str(rdata.address)
        elif record_type == 'CNAME':
            return str(rdata.target)
        elif record_type == 'MX':
            return f"{rdata.preference} {rdata.exchange}"
        elif record_type == 'TXT':
            # Join multiple strings in TXT record
            txt_strings = [s.decode('utf-8', errors='replace') if isinstance(s, bytes) else str(s) for s in rdata.strings]
            return ' '.join(txt_strings)
        elif record_type == 'NS':
            return str(rdata.target)
        elif record_type == 'SOA':
            return f"{rdata.mname} {rdata.rname} {rdata.serial} {rdata.refresh} {rdata.retry} {rdata.expire} {rdata.minimum}"
        elif record_type == 'PTR':
            return str(rdata.target)
        elif record_type == 'SRV':
            return f"{rdata.priority} {rdata.weight} {rdata.port} {rdata.target}"
        elif record_type == 'CAA':
            flags = rdata.flags
            tag = rdata.tag.decode('utf-8') if isinstance(rdata.tag, bytes) else str(rdata.tag)
            value = rdata.value.decode('utf-8', errors='replace') if isinstance(rdata.value, bytes) else str(rdata.value)
            return f"{flags} {tag} {value}"
        elif record_type in ['DNSKEY', 'DS']:
            return str(rdata)
        elif record_type == 'NAPTR':
            return f"{rdata.order} {rdata.preference} {rdata.flags} {rdata.service} {rdata.regexp} {rdata.replacement}"
        else:
            return str(rdata)
    except Exception as e:
        logger.debug(f'Error formatting {record_type} record: {e}')
        return str(rdata)


@plugin.command('dns')
@plugin.example('.dns example.com')
@plugin.example('.dns example.com A')
@plugin.example('.dns example.com MX')
def dns_query(bot, trigger):
    """Query DNS records. Usage: .dns <domain> [record_type]"""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .dns <domain> [record_type]')
        bot.notice(trigger.nick, 'Record types: A, AAAA, CNAME, MX, TXT, NS, SOA, PTR, SRV, CAA, DNSKEY, DS, NAPTR, etc.')
        return
    
    args = trigger.group(2).strip().split()
    domain = args[0]
    record_type = args[1].upper() if len(args) > 1 else 'A'
    
    if record_type not in RECORD_TYPES:
        bot.notice(trigger.nick, f'Unsupported record type: {record_type}')
        bot.notice(trigger.nick, f'Supported types: {", ".join(sorted(RECORD_TYPES.keys()))}')
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


@plugin.command('dns_dot')
@plugin.example('.dns_dot example.com')
@plugin.example('.dns_dot example.com A cloudflare')
def dns_dot(bot, trigger):
    """Query DNS over TLS. Usage: .dns_dot <domain> [record_type] [provider]"""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .dns_dot <domain> [record_type] [provider]')
        bot.notice(trigger.nick, f'Providers: {", ".join(sorted(DOT_PROVIDERS.keys()))}')
        return
    
    args = trigger.group(2).strip().split()
    domain = args[0]
    record_type = args[1].upper() if len(args) > 1 else 'A'
    provider_key = args[2].lower() if len(args) > 2 else 'cloudflare'
    
    if record_type not in RECORD_TYPES:
        bot.notice(trigger.nick, f'Unsupported record type: {record_type}')
        return
    
    if provider_key not in DOT_PROVIDERS:
        bot.notice(trigger.nick, f'Unknown provider: {provider_key}')
        bot.notice(trigger.nick, f'Available providers: {", ".join(sorted(DOT_PROVIDERS.keys()))}')
        return
    
    provider = DOT_PROVIDERS[provider_key]
    
    try:
        response = query_dot(domain, record_type, provider['hostname'], provider['port'])
        if not response:
            bot.notice(trigger.nick, f'No {record_type} records found for {domain} via {provider["name"]}')
            return
        
        formatted = format_dns_response(response, record_type)
        bot.say(f"{formatter.bold(domain)} {record_type} via {formatter.italic(provider['name'])}: {formatted}")
    except Exception as e:
        logger.exception('DoT query error', e)
        bot.notice(trigger.nick, f'DoT query failed: {e}')


@plugin.command('dns_rr')
@plugin.example('.dns_rr example.com')
@plugin.example('.dns_rr example.com AAAA')
def dns_roundrobin(bot, trigger):
    """Query DNS using round-robin DoTLS resolver. Usage: .dns_rr <domain> [record_type]"""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .dns_rr <domain> [record_type]')
        return
    
    args = trigger.group(2).strip().split()
    domain = args[0]
    record_type = args[1].upper() if len(args) > 1 else 'A'
    
    if record_type not in RECORD_TYPES:
        bot.notice(trigger.nick, f'Unsupported record type: {record_type}')
        return
    
    try:
        response, provider = roundrobin_resolver.query(domain, record_type)
        if not response:
            bot.notice(trigger.nick, f'No {record_type} records found for {domain}')
            return
        
        formatted = format_dns_response(response, record_type)
        bot.say(f"{formatter.bold(domain)} {record_type} via {formatter.italic(provider['name'])} (round-robin): {formatted}")
    except Exception as e:
        logger.exception('Round-robin DoT query error', e)
        bot.notice(trigger.nick, f'Round-robin DoT query failed: {e}')


@plugin.command('dns_anycast')
@plugin.example('.dns_anycast example.com')
@plugin.example('.dns_anycast example.com MX')
def dns_anycast(bot, trigger):
    """Query DNS using anycast DoTLS resolver (first working provider). Usage: .dns_anycast <domain> [record_type]"""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .dns_anycast <domain> [record_type]')
        return
    
    args = trigger.group(2).strip().split()
    domain = args[0]
    record_type = args[1].upper() if len(args) > 1 else 'A'
    
    if record_type not in RECORD_TYPES:
        bot.notice(trigger.nick, f'Unsupported record type: {record_type}')
        return
    
    try:
        provider = anycast_resolver.get_fastest()
        response = query_dot(domain, record_type, provider['hostname'], provider['port'])
        if not response:
            bot.notice(trigger.nick, f'No {record_type} records found for {domain}')
            return
        
        latency = anycast_resolver.latencies.get(provider['name'], 0)
        formatted = format_dns_response(response, record_type)
        bot.say(f"{formatter.bold(domain)} {record_type} via {formatter.italic(provider['name'])} (anycast, {formatter.underline(f'{latency:.1f}ms')}): {formatted}")
    except Exception as e:
        logger.exception('Anycast DoT query error', e)
        bot.notice(trigger.nick, f'Anycast DoT query failed: {e}')


@plugin.command('dns_xfr')
@plugin.example('.dns_xfr example.com nameserver.example.com')
def dns_xfr(bot, trigger):
    """Perform DNS zone transfer (XFR) over TLS. Usage: .dns_xfr <zone> <nameserver>"""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .dns_xfr <zone> <nameserver>')
        bot.notice(trigger.nick, 'Example: .dns_xfr example.com ns1.example.com')
        return
    
    args = trigger.group(2).strip().split()
    if len(args) < 2:
        bot.notice(trigger.nick, 'Usage: .dns_xfr <zone> <nameserver>')
        return
    
    zone = args[0]
    nameserver = args[1]
    
    try:
        # Perform zone transfer over TLS
        query = dns.message.make_query(zone, dns.rdatatype.AXFR)
        response = dns.query.tls(query, nameserver, port=853, timeout=30.0)
        
        if not response or not response.answer:
            bot.notice(trigger.nick, f'Zone transfer failed or returned no records for {zone}')
            return
        
        # Count records
        record_count = sum(len(rrset) for rrset in response.answer)
        bot.say(f"{formatter.bold(zone)} zone transfer via {formatter.italic(nameserver)}: {formatter.underline(str(record_count))} record(s)")
        
        # Show first few records
        shown = 0
        for rrset in response.answer[:5]:
            for rdata in rrset[:3]:
                if shown >= 5:
                    break
                formatted = format_rdata(rdata, rrset.rdtype.name)
                bot.say(f"  {rrset.name} {rrset.rdtype.name}: {formatted}")
                shown += 1
        
        if record_count > 5:
            bot.say(f"... and {record_count - 5} more records")
    except dns.exception.FormError:
        bot.notice(trigger.nick, f'Zone transfer not allowed for {zone} (likely ACL restriction)')
    except Exception as e:
        logger.exception('Zone transfer error', e)
        bot.notice(trigger.nick, f'Zone transfer failed: {e}')


@plugin.command('dns_providers')
def dns_providers(bot, trigger):
    """List all available DoT providers."""
    bot.say(f'Available DoT providers ({len(DOT_PROVIDERS)}):')
    for key, provider in sorted(DOT_PROVIDERS.items()):
        bot.say(f"{formatter.bold(key)}: {provider['name']} ({provider['hostname']}:{provider['port']})")


def setup(bot):
    """Module setup - DNS module loaded."""
    bot.memory['dns_loaded'] = True
    bot.memory['dns_providers'] = len(DOT_PROVIDERS)
    bot.memory['dns_record_types'] = len(RECORD_TYPES)
    logger.info('DNS module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['dns_loaded'] = False
    logger.info('DNS module unloaded')

