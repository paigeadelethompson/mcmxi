"""
Sopel module for URL Shorteners APIs.
Supports 6 public APIs with no authentication required.
"""

from sopel import plugin
import json
import sys
import os
from typing import Optional
# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get_module_logger, HTTPClient, IRCFormatter

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)
formatter = IRCFormatter()


# Utility functions for other modules to use
def shorten_cleanuri(url: str) -> Optional[str]:
    """
    Shorten URL using CleanURI API.
    Returns shortened URL or None on error.
    """
    try:
        api_url = 'https://cleanuri.com/api/v1/shorten'
        post_data = http.urlencode({'url': url}).encode('utf-8')
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        data = http.post(api_url, data=post_data, headers=headers)
        
        if data and 'result_url' in data:
            return data.get('result_url')
    except Exception as e:
        logger.exception('Error shortening URL with CleanURI', exc_info=e)
    return None


def shorten_spoo(url: str, alias: Optional[str] = None) -> Optional[str]:
    """
    Shorten URL using Spoo.me API.
    Returns shortened URL or None on error.
    """
    try:
        api_url = 'https://spoo.me/api/v1/shorten'
        payload = {'url': url}
        if alias:
            payload['alias'] = alias
        
        headers = {'Content-Type': 'application/json'}
        post_data = json.dumps(payload).encode('utf-8')
        data = http.post(api_url, data=post_data, headers=headers)
        
        if data and 'short_url' in data:
            return data.get('short_url')
    except Exception as e:
        logger.exception('Error shortening URL with Spoo.me', exc_info=e)
    return None


def shorten_isgd(url: str) -> Optional[str]:
    """
    Shorten URL using is.gd API.
    Returns shortened URL or None on error.
    """
    try:
        api_url = f'https://is.gd/create.php?format=json&url={http.quote(url)}'
        data = http.get(api_url)
        
        if data and 'shorturl' in data:
            return data.get('shorturl')
    except Exception as e:
        logger.exception('Error shortening URL with is.gd', exc_info=e)
    return None


def shorten_vgd(url: str) -> Optional[str]:
    """
    Shorten URL using v.gd API.
    Returns shortened URL or None on error.
    """
    try:
        api_url = f'https://v.gd/create.php?format=json&url={http.quote(url)}'
        data = http.get(api_url)
        
        if data and 'shorturl' in data:
            return data.get('shorturl')
    except Exception as e:
        logger.exception('Error shortening URL with v.gd', exc_info=e)
    return None


def shorten_tinyurl(url: str) -> Optional[str]:
    """
    Shorten URL using TinyURL API.
    Returns shortened URL or None on error.
    """
    try:
        api_url = f'https://tinyurl.com/api-create.php?url={http.quote(url)}'
        # TinyURL returns plain text, not JSON - use get_text which handles non-JSON
        response = http.get_text(api_url)
        
        if response and response.startswith('http'):
            # Strip any whitespace/newlines
            return response.strip()
    except Exception as e:
        logger.exception('Error shortening URL with TinyURL', exc_info=e)
    return None


def shorten_clcis(url: str, slug: Optional[str] = None) -> Optional[str]:
    """
    Shorten URL using CLC.IS API.
    Returns shortened URL or None on error.
    """
    try:
        api_url = 'https://clc.is/api/links'
        payload = {'domain': 'clc.is', 'target_url': url}
        if slug:
            payload['slug'] = slug
        
        headers = {'Content-Type': 'application/json'}
        post_data = json.dumps(payload).encode('utf-8')
        data = http.post(api_url, data=post_data, headers=headers)
        
        # CLC.IS returns an array with one object
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
            if 'url' in item:
                return item.get('url')
        elif isinstance(data, dict) and 'url' in data:
            return data.get('url')
    except Exception as e:
        logger.exception('Error shortening URL with CLC.IS', exc_info=e)
    return None


# Available services in order
_SHORTENER_SERVICES = ['cleanuri', 'spoo', 'isgd', 'vgd', 'tinyurl', 'clcis']
_RR_INDEX = 0  # Round-robin index (module-level state)


def shorten_url_anycast(url: str) -> Optional[str]:
    """
    Anycast URL shortening - tries all services in parallel/first-success order.
    Returns the first successful shortened URL or None if all fail.
    """
    services = _SHORTENER_SERVICES.copy()
    
    # Try services in order, return first success
    for service in services:
        try:
            result = shorten_url(url, service=service)
            if result:
                logger.info(f'Anycast success with {service}')
                return result
        except Exception as e:
            logger.debug(f'Anycast failed for {service}: {e}')
            continue
    
    logger.warning(f'Anycast failed for all services')
    return None


def shorten_url_roundrobin(url: str) -> Optional[str]:
    """
    Round-robin URL shortening - cycles through all services.
    Returns shortened URL or None on error.
    """
    global _RR_INDEX
    
    # Get next service in round-robin
    service = _SHORTENER_SERVICES[_RR_INDEX]
    _RR_INDEX = (_RR_INDEX + 1) % len(_SHORTENER_SERVICES)
    
    logger.info(f'Round-robin using {service} (index {_RR_INDEX})')
    return shorten_url(url, service=service)


def shorten_url(url: str, service: str = 'cleanuri') -> Optional[str]:
    """
    Universal URL shortening function.
    Supports: 'cleanuri', 'spoo', 'isgd', 'vgd', 'tinyurl', 'clcis'
    Returns shortened URL or None on error.
    """
    service = service.lower()
    
    if service == 'cleanuri':
        return shorten_cleanuri(url)
    elif service == 'spoo':
        return shorten_spoo(url)
    elif service == 'isgd' or service == 'is.gd':
        return shorten_isgd(url)
    elif service == 'vgd' or service == 'v.gd':
        return shorten_vgd(url)
    elif service == 'tinyurl':
        return shorten_tinyurl(url)
    elif service == 'clcis' or service == 'clc.is':
        return shorten_clcis(url)
    else:
        logger.warning(f'Unknown URL shortening service: {service}')
        return None


# API definitions
APIS = [
    {
        'name': '1pt',
        'description': 'A simple URL shortener',
        'link': 'https://github.com/1pt-co/api/blob/main/README.md',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'CleanURI',
        'description': 'URL shortener service',
        'link': 'https://cleanuri.com/docs',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Free Url Shortener',
        'description': 'Free URL Shortener offers a powerful API to interact with other sites',
        'link': 'https://ulvis.net/developer.html',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Mgnet.me',
        'description': 'Torrent URL shorten API',
        'link': 'http://mgnet.me/api.html',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Spoo.me',
        'description': 'Free URL shortener with custom alias, max-clicks, password protection and advanced analytics support',
        'link': 'https://spoo.me/api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Urlmskr',
        'description': 'Easy and fast masked, shortened link creation',
        'link': 'https://github.com/Axorax/urlmskr#urlmskr-api',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('url_shorteners')
@plugin.command('urlshorteners')
@plugin.example(f'.url_shorteners')
def url_shorteners_list(bot, trigger):
    """List all available URL Shorteners APIs."""
    bot.say(f'Available URL Shorteners APIs (6):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .url_shorteners_info <name> for details')


@plugin.command('url_shorteners_info')
@plugin.example(f'.url_shorteners_info <name>')
def url_shorteners_info(bot, trigger):
    """Get information about a specific URL Shorteners API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .url_shorteners_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('url_shorteners_search')
@plugin.example(f'.url_shorteners_search <query>')
def url_shorteners_search(bot, trigger):
    """Search URL Shorteners APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .url_shorteners_search <query>')
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
    for api in results[:5]:  # Show first 5 results
        bot.say(f"- {api['name']}: {api['description'][:60]}")
    if len(results) > 5:
        bot.say(f'... and {len(results) - 5} more results')


@plugin.command('shorten_cleanuri')
@plugin.example('.shorten_cleanuri https://example.com')
def shorten_cleanuri_cmd(bot, trigger):
    """Shorten URL using CleanURI API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .shorten_cleanuri <url>')
        bot.notice(trigger.nick, 'Example: .shorten_cleanuri https://example.com')
        return
    
    url = trigger.group(2).strip()
    logger.info(f'URL shortening: {url}')
    
    short_url = shorten_cleanuri(url)
    
    if not short_url:
        bot.notice(trigger.nick, 'Failed to shorten URL or API error.')
        return
    
    response = f"Shortened: {formatter.bold(short_url)}"
    response += f" | Original: {formatter.monospace(url)}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('shorten_spoo')
@plugin.example('.shorten_spoo https://example.com')
@plugin.example('.shorten_spoo https://example.com myalias')
def shorten_spoo_cmd(bot, trigger):
    """Shorten URL using Spoo.me API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .shorten_spoo <url> [alias]')
        bot.notice(trigger.nick, 'Example: .shorten_spoo https://example.com')
        bot.notice(trigger.nick, 'Example: .shorten_spoo https://example.com myalias')
        return
    
    parts = trigger.group(2).strip().split(None, 1)
    url = parts[0].strip()
    alias = parts[1].strip() if len(parts) > 1 else None
    
    logger.info(f'URL shortening with Spoo.me: {url}')
    
    short_url = shorten_spoo(url, alias=alias)
    
    if not short_url:
        bot.notice(trigger.nick, 'Failed to shorten URL or API error.')
        return
    
    response = f"Shortened: {formatter.bold(short_url)}"
    response += f" | Original: {formatter.monospace(url)}"
    if alias:
        response += f" | Alias: {formatter.monospace(alias)}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('shorten_isgd')
@plugin.example('.shorten_isgd https://example.com')
def shorten_isgd_cmd(bot, trigger):
    """Shorten URL using is.gd API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .shorten_isgd <url>')
        bot.notice(trigger.nick, 'Example: .shorten_isgd https://example.com')
        return
    
    url = trigger.group(2).strip()
    logger.info(f'URL shortening with is.gd: {url}')
    
    short_url = shorten_isgd(url)
    
    if not short_url:
        bot.notice(trigger.nick, 'Failed to shorten URL or API error.')
        return
    
    response = f"Shortened: {formatter.bold(short_url)}"
    response += f" | Original: {formatter.monospace(url)}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('shorten_vgd')
@plugin.example('.shorten_vgd https://example.com')
def shorten_vgd_cmd(bot, trigger):
    """Shorten URL using v.gd API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .shorten_vgd <url>')
        bot.notice(trigger.nick, 'Example: .shorten_vgd https://example.com')
        return
    
    url = trigger.group(2).strip()
    logger.info(f'URL shortening with v.gd: {url}')
    
    short_url = shorten_vgd(url)
    
    if not short_url:
        bot.notice(trigger.nick, 'Failed to shorten URL or API error.')
        return
    
    response = f"Shortened: {formatter.bold(short_url)}"
    response += f" | Original: {formatter.monospace(url)}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('shorten_tinyurl')
@plugin.example('.shorten_tinyurl https://example.com')
def shorten_tinyurl_cmd(bot, trigger):
    """Shorten URL using TinyURL API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .shorten_tinyurl <url>')
        bot.notice(trigger.nick, 'Example: .shorten_tinyurl https://example.com')
        return
    
    url = trigger.group(2).strip()
    logger.info(f'URL shortening with TinyURL: {url}')
    
    short_url = shorten_tinyurl(url)
    
    if not short_url:
        bot.notice(trigger.nick, 'Failed to shorten URL or API error.')
        return
    
    response = f"Shortened: {formatter.bold(short_url)}"
    response += f" | Original: {formatter.monospace(url)}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('shorten_clcis')
@plugin.example('.shorten_clcis https://example.com')
@plugin.example('.shorten_clcis https://example.com myslug')
def shorten_clcis_cmd(bot, trigger):
    """Shorten URL using CLC.IS API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .shorten_clcis <url> [slug]')
        bot.notice(trigger.nick, 'Example: .shorten_clcis https://example.com')
        bot.notice(trigger.nick, 'Example: .shorten_clcis https://example.com myslug')
        return
    
    parts = trigger.group(2).strip().split(None, 1)
    url = parts[0].strip()
    slug = parts[1].strip() if len(parts) > 1 else None
    
    logger.info(f'URL shortening with CLC.IS: {url}')
    
    short_url = shorten_clcis(url, slug=slug)
    
    if not short_url:
        bot.notice(trigger.nick, 'Failed to shorten URL or API error.')
        return
    
    response = f"Shortened: {formatter.bold(short_url)}"
    response += f" | Original: {formatter.monospace(url)}"
    if slug:
        response += f" | Slug: {formatter.monospace(slug)}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('shorten_anycast')
@plugin.example('.shorten_anycast https://example.com')
def shorten_anycast_cmd(bot, trigger):
    """Shorten URL using anycast (tries all services, returns first success)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .shorten_anycast <url>')
        bot.notice(trigger.nick, 'Example: .shorten_anycast https://example.com')
        bot.notice(trigger.nick, 'Tries all services and returns the first successful result.')
        return
    
    url = trigger.group(2).strip()
    logger.info(f'Anycast URL shortening: {url}')
    
    short_url = shorten_url_anycast(url)
    
    if not short_url:
        bot.notice(trigger.nick, 'Failed to shorten URL with all services.')
        return
    
    response = f"Shortened (anycast): {formatter.bold(short_url)}"
    response += f" | Original: {formatter.monospace(url)}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('shorten_rr')
@plugin.command('shorten_roundrobin')
@plugin.example('.shorten_rr https://example.com')
def shorten_roundrobin_cmd(bot, trigger):
    """Shorten URL using round-robin (cycles through all services)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .shorten_rr <url>')
        bot.notice(trigger.nick, 'Example: .shorten_rr https://example.com')
        bot.notice(trigger.nick, 'Cycles through all services for load balancing.')
        return
    
    url = trigger.group(2).strip()
    logger.info(f'Round-robin URL shortening: {url}')
    
    # Get current service before round-robin advances
    global _RR_INDEX
    current_service = _SHORTENER_SERVICES[_RR_INDEX]
    
    short_url = shorten_url_roundrobin(url)
    
    if not short_url:
        bot.notice(trigger.nick, f'Failed to shorten URL with {current_service}.')
        return
    
    response = f"Shortened ({current_service}, round-robin): {formatter.bold(short_url)}"
    response += f" | Original: {formatter.monospace(url)}"
    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('shorten')
@plugin.example('.shorten https://example.com')
@plugin.example('.shorten https://example.com spoo')
def shorten(bot, trigger):
    """Shorten URL using available services (default: cleanuri)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .shorten <url> [service]')
        bot.notice(trigger.nick, 'Example: .shorten https://example.com')
        bot.notice(trigger.nick, 'Example: .shorten https://example.com spoo')
        bot.notice(trigger.nick, 'Available services: cleanuri, spoo, isgd, vgd, tinyurl, clcis, anycast, roundrobin')
        return
    
    parts = trigger.group(2).strip().split(None, 1)
    url = parts[0].strip()
    service = parts[1].strip().lower() if len(parts) > 1 else 'cleanuri'
    
    valid_services = ['cleanuri', 'spoo', 'isgd', 'is.gd', 'vgd', 'v.gd', 'tinyurl', 'clcis', 'clc.is', 'anycast', 'roundrobin', 'rr']
    
    # Handle special cases
    if service in ['anycast']:
        short_url = shorten_url_anycast(url)
        if not short_url:
            bot.notice(trigger.nick, 'Failed to shorten URL with all services.')
            return
        response = f"Shortened (anycast): {formatter.bold(short_url)}"
        response += f" | Original: {formatter.monospace(url)}"
        bot.say(formatter.truncate(response, max_len=400))
        return
    
    if service in ['roundrobin', 'rr']:
        global _RR_INDEX
        current_service = _SHORTENER_SERVICES[_RR_INDEX]
        short_url = shorten_url_roundrobin(url)
        if not short_url:
            bot.notice(trigger.nick, f'Failed to shorten URL with {current_service}.')
            return
        response = f"Shortened ({current_service}, round-robin): {formatter.bold(short_url)}"
        response += f" | Original: {formatter.monospace(url)}"
        bot.say(formatter.truncate(response, max_len=400))
        return
    
    if service not in valid_services:
        bot.notice(trigger.nick, f'Invalid service. Available: cleanuri, spoo, isgd, vgd, tinyurl, clcis, anycast, roundrobin')
        return
    
    logger.info(f'URL shortening with {service}: {url}')
    
    short_url = shorten_url(url, service=service)
    
    if not short_url:
        bot.notice(trigger.nick, f'Failed to shorten URL with {service}.')
        return
    
    response = f"Shortened ({service}): {formatter.bold(short_url)}"
    response += f" | Original: {formatter.monospace(url)}"
    bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - URL Shorteners APIs loaded."""
    bot.memory['url_shorteners_loaded'] = True
    bot.memory['url_shorteners_count'] = 6
    logger.info('URL Shorteners module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['url_shorteners_loaded'] = False
    logger.info('URL Shorteners module unloaded')
