"""
Sopel module for WiGLE (Wireless Geographic Logging Engine) API.
Supports WiFi network lookups by BSSID/MAC address, SSID, and location.
Requires API authentication via config.
"""
import base64
import os
import sys
from typing import Dict, Optional

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, IRCFormatter, get_command_prefix, get_module_logger

logger = get_module_logger(__name__)
http = HTTPClient(max_size=1 * 1024 * 1024)  # 1MB max
formatter = IRCFormatter()

# WiGLE API endpoint
WIGLE_API_URL = 'https://api.wigle.net/api/v2'


def get_auth_headers(bot) -> Optional[Dict[str, str]]:
    """Get authentication headers for WiGLE API."""
    try:
        api_name = bot.config.wigle.api_name
        api_token = bot.config.wigle.api_token
        if not api_name or not api_token:
            return None
        
        # WiGLE uses HTTP Basic Auth with API name as username and token as password
        credentials = f'{api_name}:{api_token}'
        encoded = base64.b64encode(credentials.encode()).decode()
        return {'Authorization': f'Basic {encoded}'}
    except Exception as e:
        logger.debug(f'Error getting WiGLE auth: {e}')
        return None


def normalize_mac(mac: str) -> str:
    """Normalize MAC address to format expected by WiGLE (XX:XX:XX:XX:XX:XX)."""
    # Remove common separators
    mac = mac.replace(':', '').replace('-', '').replace('.', '').upper()
    
    # Validate length (should be 12 hex characters)
    if len(mac) != 12:
        return mac
    
    # Format as XX:XX:XX:XX:XX:XX
    return ':'.join(mac[i:i+2] for i in range(0, 12, 2))


def lookup_network_by_bssid(bot, bssid: str) -> Optional[Dict]:
    """Lookup WiFi network by BSSID/MAC address."""
    bssid = normalize_mac(bssid)
    
    if len(bssid) != 17:  # XX:XX:XX:XX:XX:XX format
        return None
    
    headers = get_auth_headers(bot)
    if not headers:
        return {'error': 'AUTH_REQUIRED'}
    
    url = f'{WIGLE_API_URL}/network/detail'
    
    logger.info(f'Looking up WiGLE network by BSSID: {bssid}')
    
    # WiGLE API requires GET with query params
    # URL encode the BSSID
    encoded_bssid = http.quote(bssid)
    full_url = f'{url}?netid={encoded_bssid}'
    response = http.get(full_url, headers=headers, timeout=10)
    
    if not response:
        logger.error('Failed to query WiGLE API')
        return None
    
    # Check for errors
    if 'error' in response:
        return response
    
    # WiGLE returns data in 'results' array
    results = response.get('results', [])
    if not results:
        return {'error': 'NOT_FOUND'}
    
    return results[0]  # Return first result


def search_networks_by_ssid(bot, ssid: str, limit: int = 5) -> Optional[Dict]:
    """Search WiFi networks by SSID."""
    headers = get_auth_headers(bot)
    if not headers:
        return {'error': 'AUTH_REQUIRED'}
    
    url = f'{WIGLE_API_URL}/network/search'
    # WiGLE API uses 'ssid' parameter for SSID search
    # URL encode the SSID
    encoded_ssid = http.quote(ssid)
    full_url = f'{url}?ssid={encoded_ssid}&resultsPerPage={limit}'
    
    logger.info(f'Searching WiGLE networks by SSID: {ssid}')
    
    response = http.get(full_url, headers=headers, timeout=10)
    
    if not response:
        logger.error('Failed to query WiGLE API')
        return None
    
    # Check for errors
    if 'error' in response:
        return response
    
    return response


def search_networks_by_location(
    bot, city: Optional[str] = None, state: Optional[str] = None,
    zipcode: Optional[str] = None, limit: int = 10
) -> Optional[Dict]:
    """Search WiFi networks by location (city, state, or zipcode)."""
    headers = get_auth_headers(bot)
    if not headers:
        return {'error': 'AUTH_REQUIRED'}
    
    if not city and not state and not zipcode:
        return {'error': 'INVALID_PARAMS'}
    
    url = f'{WIGLE_API_URL}/network/search'
    params = []
    
    if city:
        # addresscode is used for city/address (max 30 chars)
        city_clean = city[:30].strip()
        params.append(f'addresscode={http.quote(city_clean)}')
    
    if state:
        # statecode is two-character state code
        state_clean = state[:2].strip().upper()
        params.append(f'statecode={http.quote(state_clean)}')
    
    if zipcode:
        # zipcode is five-digit ZIP code
        zip_clean = zipcode[:5].strip()
        params.append(f'zipcode={http.quote(zip_clean)}')
    
    params.append(f'resultsPerPage={limit}')
    full_url = f'{url}?{"&".join(params)}'
    
    logger.info(
        f'Searching WiGLE networks by location: '
        f'city={city}, state={state}, zipcode={zipcode}'
    )
    
    response = http.get(full_url, headers=headers, timeout=10)
    
    if not response:
        logger.error('Failed to query WiGLE API')
        return None
    
    # Check for errors
    if 'error' in response:
        return response
    
    return response


@plugin.command('wigle_bssid')
@plugin.example('`wigle_bssid 00:11:22:33:44:55')
@plugin.example('`wigle_bssid 00-11-22-33-44-55')
def wigle_bssid(bot, trigger):
    """Lookup WiFi network by BSSID/MAC address using WiGLE."""
    prefix = get_command_prefix(bot)
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: {prefix}wigle_bssid <BSSID>')
        bot.notice(trigger.nick, f'Example: {prefix}wigle_bssid 00:11:22:33:44:55')
        return
    
    bssid = trigger.group(2).strip()
    
    data = lookup_network_by_bssid(bot, bssid)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to query WiGLE API')
        return
    
    if 'error' in data:
        if data['error'] == 'AUTH_REQUIRED':
            bot.notice(
                trigger.nick,
                'WiGLE API authentication required. Configure api_name and api_token in [wigle] section.'
            )
        elif data['error'] == 'NOT_FOUND':
            bot.notice(trigger.nick, f'Network with BSSID {bssid} not found in WiGLE database')
        else:
            bot.notice(trigger.nick, f'WiGLE API error: {data["error"]}')
        return
    
    # Display network information
    ssid = data.get('ssid', 'Unknown')
    bssid_display = data.get('netid', bssid)
    bot.say(
        f"{formatter.bold('Network')}: {formatter.monospace(ssid)} "
        f"({formatter.monospace(bssid_display)})"
    )
    
    # Channel and frequency
    channel = data.get('channel', '')
    frequency = data.get('frequency', '')
    if channel:
        bot.say(f"{formatter.bold('Channel')}: {formatter.monospace(channel)}")
    if frequency:
        bot.say(f"{formatter.bold('Frequency')}: {formatter.monospace(frequency)} MHz")
    
    # Encryption
    encryption = data.get('encryption', '')
    if encryption:
        bot.say(f"{formatter.bold('Encryption')}: {encryption}")
    
    # Location
    latitude = data.get('trilat', '')
    longitude = data.get('trilong', '')
    if latitude and longitude:
        bot.say(
            f"{formatter.bold('Location')}: "
            f"{formatter.monospace(f'{latitude},{longitude}')}"
        )
    
    # First and last seen
    first_seen = data.get('firsttime', '')
    last_seen = data.get('lasttime', '')
    if first_seen:
        bot.say(f"{formatter.bold('First Seen')}: {first_seen}")
    if last_seen:
        bot.say(f"{formatter.bold('Last Seen')}: {last_seen}")
    
    # WiGLE page link
    if bssid_display:
        bot.say(f"WiGLE: https://wigle.net/map?netid={bssid_display}")


@plugin.command('wigle_ssid')
@plugin.example('`wigle_ssid Linksys')
@plugin.example('`wigle_ssid "My Network"')
def wigle_ssid(bot, trigger):
    """Search WiFi networks by SSID using WiGLE."""
    prefix = get_command_prefix(bot)
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: {prefix}wigle_ssid <SSID>')
        bot.notice(trigger.nick, f'Example: {prefix}wigle_ssid Linksys')
        return
    
    ssid = trigger.group(2).strip()
    
    data = search_networks_by_ssid(bot, ssid, limit=5)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to query WiGLE API')
        return
    
    if 'error' in data:
        if data['error'] == 'AUTH_REQUIRED':
            bot.notice(
                trigger.nick,
                'WiGLE API authentication required. Configure api_name and api_token in [wigle] section.'
            )
        else:
            bot.notice(trigger.nick, f'WiGLE API error: {data["error"]}')
        return
    
    # WiGLE returns results in 'results' array
    results = data.get('results', [])
    total = data.get('totalResults', len(results))
    
    if not results:
        bot.notice(trigger.nick, f'No networks found with SSID "{ssid}"')
        return
    
    bot.say(
        f"{formatter.bold('WiGLE Search Results')} for "
        f"{formatter.monospace(ssid)} "
        f"({formatter.underline(str(len(results)))} of {total} shown):"
    )
    
    for i, network in enumerate(results[:5], 1):
        network_ssid = network.get('ssid', 'Unknown')
        bssid = network.get('netid', 'Unknown')
        encryption = network.get('encryption', '')
        channel = network.get('channel', '')
        
        response_parts = [
            f"{i}. {formatter.bold(network_ssid)}",
            f"BSSID: {formatter.monospace(bssid)}"
        ]
        
        if encryption:
            response_parts.append(f"Enc: {encryption}")
        if channel:
            response_parts.append(f"Ch: {channel}")
        
        bot.say(' | '.join(response_parts))
    
    if total > 5:
        bot.say(f"... and {total - 5} more results")


@plugin.command('wigle_city')
@plugin.example('`wigle_city Boston MA')
@plugin.example('`wigle_city "New York" NY')
def wigle_city(bot, trigger):
    """Search WiFi networks by city and state using WiGLE."""
    prefix = get_command_prefix(bot)
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: {prefix}wigle_city <city> <state>')
        bot.notice(trigger.nick, f'Example: {prefix}wigle_city Boston MA')
        return
    
    args = trigger.group(2).strip().split(None, 1)
    if len(args) < 2:
        bot.notice(trigger.nick, f'Usage: {prefix}wigle_city <city> <state>')
        bot.notice(trigger.nick, f'Example: {prefix}wigle_city Boston MA')
        return
    
    city = args[0].strip()
    state = args[1].strip()
    
    data = search_networks_by_location(bot, city=city, state=state, limit=10)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to query WiGLE API')
        return
    
    if 'error' in data:
        if data['error'] == 'AUTH_REQUIRED':
            bot.notice(
                trigger.nick,
                'WiGLE API authentication required. Configure api_name and api_token in [wigle] section.'
            )
        elif data['error'] == 'INVALID_PARAMS':
            bot.notice(trigger.nick, 'Invalid parameters provided')
        else:
            bot.notice(trigger.nick, f'WiGLE API error: {data["error"]}')
        return
    
    # WiGLE returns results in 'results' array
    results = data.get('results', [])
    total = data.get('totalResults', len(results))
    
    if not results:
        bot.notice(
            trigger.nick,
            f'No networks found in {city}, {state}'
        )
        return
    
    bot.say(
        f"{formatter.bold('WiGLE Search Results')} for "
        f"{formatter.monospace(city)}, {formatter.monospace(state)} "
        f"({formatter.underline(str(len(results)))} of {total} shown):"
    )
    
    for i, network in enumerate(results[:10], 1):
        network_ssid = network.get('ssid', 'Unknown')
        bssid = network.get('netid', 'Unknown')
        encryption = network.get('encryption', '')
        channel = network.get('channel', '')
        
        response_parts = [
            f"{i}. {formatter.bold(network_ssid)}",
            f"BSSID: {formatter.monospace(bssid)}"
        ]
        
        if encryption:
            response_parts.append(f"Enc: {encryption}")
        if channel:
            response_parts.append(f"Ch: {channel}")
        
        bot.say(' | '.join(response_parts))
    
    if total > 10:
        bot.say(f"... and {total - 10} more results")


@plugin.command('wigle_zip')
@plugin.example('`wigle_zip 02134')
@plugin.example('`wigle_zip 10001')
def wigle_zip(bot, trigger):
    """Search WiFi networks by ZIP code using WiGLE."""
    prefix = get_command_prefix(bot)
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: {prefix}wigle_zip <zipcode>')
        bot.notice(trigger.nick, f'Example: {prefix}wigle_zip 02134')
        return
    
    zipcode = trigger.group(2).strip()
    
    # Validate ZIP code format (should be 5 digits)
    if not zipcode.isdigit() or len(zipcode) != 5:
        bot.notice(trigger.nick, 'ZIP code must be 5 digits')
        return
    
    data = search_networks_by_location(bot, zipcode=zipcode, limit=10)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to query WiGLE API')
        return
    
    if 'error' in data:
        if data['error'] == 'AUTH_REQUIRED':
            bot.notice(
                trigger.nick,
                'WiGLE API authentication required. Configure api_name and api_token in [wigle] section.'
            )
        elif data['error'] == 'INVALID_PARAMS':
            bot.notice(trigger.nick, 'Invalid parameters provided')
        else:
            bot.notice(trigger.nick, f'WiGLE API error: {data["error"]}')
        return
    
    # WiGLE returns results in 'results' array
    results = data.get('results', [])
    total = data.get('totalResults', len(results))
    
    if not results:
        bot.notice(trigger.nick, f'No networks found in ZIP code {zipcode}')
        return
    
    bot.say(
        f"{formatter.bold('WiGLE Search Results')} for ZIP code "
        f"{formatter.monospace(zipcode)} "
        f"({formatter.underline(str(len(results)))} of {total} shown):"
    )
    
    for i, network in enumerate(results[:10], 1):
        network_ssid = network.get('ssid', 'Unknown')
        bssid = network.get('netid', 'Unknown')
        encryption = network.get('encryption', '')
        channel = network.get('channel', '')
        
        response_parts = [
            f"{i}. {formatter.bold(network_ssid)}",
            f"BSSID: {formatter.monospace(bssid)}"
        ]
        
        if encryption:
            response_parts.append(f"Enc: {encryption}")
        if channel:
            response_parts.append(f"Ch: {channel}")
        
        bot.say(' | '.join(response_parts))
    
    if total > 10:
        bot.say(f"... and {total - 10} more results")


def setup(bot):
    """Module setup - WiGLE module loaded."""
    bot.memory['wigle_loaded'] = True
    logger.info('WiGLE module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['wigle_loaded'] = False
    logger.info('WiGLE module unloaded')

