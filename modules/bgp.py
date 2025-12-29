"""
Sopel module for BGP/RIPE database queries.
Downloads and queries RIPE database from https://ftp.ripe.net/ripe/dbase/
"""
import gzip
import ipaddress
import os
import re
import sys
import threading
from typing import Dict, List, Optional

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, IRCFormatter, get_module_logger

logger = get_module_logger(__name__)
http = HTTPClient(max_size=500 * 1024 * 1024)  # 500MB max for database
formatter = IRCFormatter()

# Database file path
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DB_FILE = os.path.join(DB_DIR, 'ripe.db.gz')
DB_URL = 'https://ftp.ripe.net/ripe/dbase/ripe.db.gz'

# Thread lock for database operations
db_lock = threading.Lock()
db_loaded = False


def ensure_db_dir():
    """Ensure database directory exists."""
    os.makedirs(DB_DIR, exist_ok=True)


def download_database(force: bool = False) -> bool:
    """Download RIPE database if it doesn't exist or force is True."""
    ensure_db_dir()
    
    if os.path.exists(DB_FILE) and not force:
        logger.info(f'RIPE database already exists: {DB_FILE}')
        return True
    
    logger.info(f'Downloading RIPE database from {DB_URL}')
    try:
        response = http.get(DB_URL)
        if not response or 'text' not in response:
            # Try to get as binary
            import urllib.request
            with urllib.request.urlopen(DB_URL) as f:
                data = f.read()
                with open(DB_FILE, 'wb') as out:
                    out.write(data)
        else:
            # If we got text, write it directly
            with open(DB_FILE, 'wb') as f:
                f.write(response['text'].encode('utf-8'))
        
        logger.info(f'RIPE database downloaded: {DB_FILE}')
        return True
    except Exception as e:
        logger.error(f'Failed to download RIPE database: {e}')
        return False


def parse_ripe_object(lines: List[str]) -> Dict[str, str]:
    """Parse a RIPE database object from lines."""
    obj = {}
    current_key = None
    current_value = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if ':' in line:
            # Save previous key-value
            if current_key:
                obj[current_key] = '\n'.join(current_value).strip()
            
            # New key-value pair
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if key in obj:
                # Multi-value field - convert to list
                if not isinstance(obj[key], list):
                    obj[key] = [obj[key]]
                obj[key].append(value)
                current_key = None
            else:
                current_key = key
                current_value = [value]
        elif current_key and line.startswith(' '):
            # Continuation line
            current_value.append(line.strip())
    
    # Save last key-value
    if current_key:
        obj[current_key] = '\n'.join(current_value).strip()
    
    return obj


def search_database(query_type: str, query_value: str, limit: int = 5) -> List[Dict[str, str]]:
    """Search RIPE database for objects matching query."""
    if not os.path.exists(DB_FILE):
        logger.warning('RIPE database not found, cannot search')
        return []
    
    results = []
    current_object = []
    in_object = False
    
    try:
        with gzip.open(DB_FILE, 'rt', encoding='latin-1', errors='ignore') as f:
            for line in f:
                line = line.rstrip('\n\r')
                
                if line.startswith('inetnum:') or line.startswith('inet6num:') or \
                   line.startswith('aut-num:') or line.startswith('organisation:') or \
                   line.startswith('person:') or line.startswith('role:'):
                    # Save previous object if it matches
                    if in_object and current_object:
                        obj = parse_ripe_object(current_object)
                        if matches_query(obj, query_type, query_value):
                            results.append(obj)
                            if len(results) >= limit:
                                break
                    
                    # Start new object
                    current_object = [line]
                    in_object = True
                elif line == '' and in_object:
                    # End of object
                    if current_object:
                        obj = parse_ripe_object(current_object)
                        if matches_query(obj, query_type, query_value):
                            results.append(obj)
                            if len(results) >= limit:
                                break
                    current_object = []
                    in_object = False
                elif in_object:
                    current_object.append(line)
            
            # Check last object
            if in_object and current_object:
                obj = parse_ripe_object(current_object)
                if matches_query(obj, query_type, query_value):
                    results.append(obj)
    
    except Exception as e:
        logger.error(f'Error reading RIPE database: {e}')
    
    return results


def matches_query(obj: Dict[str, str], query_type: str, query_value: str) -> bool:
    """Check if object matches query."""
    query_value_lower = query_value.lower()
    
    if query_type == 'asn':
        # Search aut-num objects
        if 'aut-num' not in obj:
            return False
        asn = obj.get('aut-num', '').upper()
        query_asn = query_value.upper().replace('AS', '')
        return query_asn in asn
    
    elif query_type == 'ip':
        # Search inetnum/inet6num objects
        if 'inetnum' not in obj and 'inet6num' not in obj:
            return False
        try:
            ip = ipaddress.ip_address(query_value)
            inetnum = obj.get('inetnum', obj.get('inet6num', ''))
            if '-' in inetnum:
                start, end = inetnum.split('-', 1)
                start_ip = ipaddress.ip_address(start.strip())
                end_ip = ipaddress.ip_address(end.strip())
                return start_ip <= ip <= end_ip
            elif '/' in inetnum:
                network = ipaddress.ip_network(inetnum, strict=False)
                return ip in network
        except (ValueError, AttributeError):
            return False
    
    elif query_type == 'org':
        # Search organisation objects
        if 'organisation' not in obj:
            return False
        org_id = obj.get('organisation', '').lower()
        org_name = obj.get('org-name', '').lower()
        return query_value_lower in org_id or query_value_lower in org_name
    
    elif query_type == 'text':
        # Search all text fields
        for value in obj.values():
            if isinstance(value, list):
                value = ' '.join(value)
            if query_value_lower in str(value).lower():
                return True
    
    return False


def format_autnum(obj: Dict[str, str]) -> str:
    """Format aut-num object for display."""
    asn = obj.get('aut-num', 'Unknown')
    as_name = obj.get('as-name', '')
    descr = obj.get('descr', '')
    org = obj.get('org', '')
    
    result = f"{formatter.bold(asn)}"
    if as_name:
        result += f": {formatter.italic(as_name)}"
    if descr:
        result += f" | {descr}"
    if org:
        result += f" | Org: {formatter.monospace(org)}"
    return result


def format_inetnum(obj: Dict[str, str]) -> str:
    """Format inetnum/inet6num object for display."""
    inetnum = obj.get('inetnum') or obj.get('inet6num', 'Unknown')
    netname = obj.get('netname', '')
    descr = obj.get('descr', '')
    country = obj.get('country', '')
    org = obj.get('org', '')
    
    result = f"{formatter.bold(inetnum)}"
    if netname:
        result += f" | {formatter.italic(netname)}"
    if descr:
        result += f" | {descr}"
    if country:
        result += f" | {formatter.monospace(country)}"
    if org:
        result += f" | Org: {formatter.monospace(org)}"
    return result


def format_organisation(obj: Dict[str, str]) -> str:
    """Format organisation object for display."""
    org_id = obj.get('organisation', 'Unknown')
    org_name = obj.get('org-name', '')
    country = obj.get('country', '')
    descr = obj.get('descr', '')
    
    result = f"{formatter.bold(org_id)}"
    if org_name:
        result += f": {formatter.italic(org_name)}"
    if descr:
        result += f" | {descr}"
    if country:
        result += f" | {formatter.monospace(country)}"
    return result


@plugin.command('ripe_update')
@plugin.example('.ripe_update')
def ripe_update(bot, trigger):
    """Update RIPE database (fantasy command)."""
    bot.say('Downloading RIPE database...')
    if download_database(force=True):
        bot.say('RIPE database updated successfully.')
    else:
        bot.say('Failed to update RIPE database.')


@plugin.command('ripe_asn')
@plugin.example('.ripe_asn AS15169')
@plugin.example('.ripe_asn 15169')
def ripe_asn(bot, trigger):
    """Query RIPE database for ASN information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .ripe_asn <ASN>')
        bot.notice(trigger.nick, 'Example: .ripe_asn AS15169')
        return
    
    asn_input = trigger.group(2).strip().upper().replace('AS', '')
    if not asn_input.isdigit():
        bot.notice(trigger.nick, 'ASN must be a number.')
        return
    
    logger.info(f'RIPE ASN lookup: {asn_input}')
    
    if not os.path.exists(DB_FILE):
        bot.notice(trigger.nick, 'RIPE database not found. Use .ripe_update to download it.')
        return
    
    results = search_database('asn', asn_input, limit=1)
    
    if not results:
        bot.notice(trigger.nick, f'ASN {asn_input} not found in RIPE database.')
        return
    
    obj = results[0]
    bot.say(format_autnum(obj))


@plugin.command('ripe_ip')
@plugin.example('.ripe_ip 8.8.8.8')
@plugin.example('.ripe_ip 2001:4860:4860::8888')
def ripe_ip(bot, trigger):
    """Query RIPE database for IP address information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .ripe_ip <ip_address>')
        bot.notice(trigger.nick, 'Example: .ripe_ip 8.8.8.8')
        return
    
    ip_input = trigger.group(2).strip()
    
    try:
        ipaddress.ip_address(ip_input)
    except ValueError:
        bot.notice(trigger.nick, 'Invalid IP address.')
        return
    
    logger.info(f'RIPE IP lookup: {ip_input}')
    
    if not os.path.exists(DB_FILE):
        bot.notice(trigger.nick, 'RIPE database not found. Use .ripe_update to download it.')
        return
    
    results = search_database('ip', ip_input, limit=1)
    
    if not results:
        bot.notice(trigger.nick, f'IP {ip_input} not found in RIPE database.')
        return
    
    obj = results[0]
    bot.say(format_inetnum(obj))


@plugin.command('ripe_org')
@plugin.example('.ripe_org GOOGLE')
@plugin.example('.ripe_org RIPE-NCC')
def ripe_org(bot, trigger):
    """Query RIPE database for organisation information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .ripe_org <org_id or org_name>')
        bot.notice(trigger.nick, 'Example: .ripe_org GOOGLE')
        return
    
    org_input = trigger.group(2).strip()
    
    logger.info(f'RIPE org lookup: {org_input}')
    
    if not os.path.exists(DB_FILE):
        bot.notice(trigger.nick, 'RIPE database not found. Use .ripe_update to download it.')
        return
    
    results = search_database('org', org_input, limit=3)
    
    if not results:
        bot.notice(trigger.nick, f'Organisation "{org_input}" not found in RIPE database.')
        return
    
    bot.say(f'Found {len(results)} organisation(s):')
    for obj in results:
        bot.say(format_organisation(obj))


@plugin.command('ripe_search')
@plugin.example('.ripe_search google')
def ripe_search(bot, trigger):
    """Search RIPE database for text matches."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .ripe_search <query>')
        bot.notice(trigger.nick, 'Example: .ripe_search google')
        return
    
    query = trigger.group(2).strip()
    
    logger.info(f'RIPE search: {query}')
    
    if not os.path.exists(DB_FILE):
        bot.notice(trigger.nick, 'RIPE database not found. Use .ripe_update to download it.')
        return
    
    results = search_database('text', query, limit=5)
    
    if not results:
        bot.notice(trigger.nick, f'No results found for "{query}".')
        return
    
    bot.say(f'Found {len(results)} result(s) for "{query}":')
    for obj in results:
        obj_type = 'inetnum' if 'inetnum' in obj else \
                   'inet6num' if 'inet6num' in obj else \
                   'aut-num' if 'aut-num' in obj else \
                   'organisation' if 'organisation' in obj else 'unknown'
        
        if obj_type in ('inetnum', 'inet6num'):
            bot.say(format_inetnum(obj))
        elif obj_type == 'aut-num':
            bot.say(format_autnum(obj))
        elif obj_type == 'organisation':
            bot.say(format_organisation(obj))
        else:
            bot.say(f"{obj_type}: {str(obj)[:200]}")


def setup(bot):
    """Module setup - download database if needed."""
    ensure_db_dir()
    if not os.path.exists(DB_FILE):
        logger.info('RIPE database not found, downloading...')
        download_database()
    bot.memory['bgp_loaded'] = True
    logger.info('BGP/RIPE module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['bgp_loaded'] = False
    logger.info('BGP/RIPE module unloaded')
