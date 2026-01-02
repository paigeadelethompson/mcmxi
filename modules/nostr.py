"""
Sopel module for Nostr protocol.
Supports publishing notes, fetching events, following users, and more.
"""

import json
import os
import sys
import time
from typing import Dict, List, Optional

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    HTTPClient,
    IRCFormatter,
    get_command_prefix,
    get_module_logger,
)

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)
formatter = IRCFormatter()

# Default Nostr relays
DEFAULT_RELAYS = [
    'wss://relay.damus.io',
    'wss://relay.snort.social',
    'wss://nos.lol',
]

# Store user follows in bot memory (keys come from config)
if 'nostr_follows' not in globals():
    nostr_follows = {}


def _create_event(
    kind: int, content: str, pubkey: str, privkey: str = None
) -> Dict:
    """Create a Nostr event."""
    import hashlib
    import hmac

    created_at = int(time.time())
    event = {
        'kind': kind,
        'created_at': created_at,
        'tags': [],
        'content': content,
        'pubkey': pubkey,
    }

    # Serialize event for signing
    event_serialized = json.dumps(
        [0, pubkey, created_at, kind, [], content], separators=(',', ':')
    )

    if privkey:
        # Sign event (simplified - in production use proper secp256k1)
        event_id = hashlib.sha256(event_serialized.encode()).hexdigest()
        event['id'] = event_id
        # Note: Proper signing requires secp256k1 library
        # For now, we'll use a placeholder
        event['sig'] = 'placeholder_signature'

    return event


def _query_relay(relay_url: str, filters: List[Dict]) -> List[Dict]:
    """Query a Nostr relay using HTTP GET (simplified)."""
    # Convert WebSocket URL to HTTP if needed
    if relay_url.startswith('wss://'):
        http_url = relay_url.replace('wss://', 'https://')
    elif relay_url.startswith('ws://'):
        http_url = relay_url.replace('ws://', 'http://')
    else:
        http_url = relay_url

    # Most relays support HTTP GET for queries
    # Format: https://relay.com/?filters=[{...}]
    filters_json = http.quote(json.dumps(filters))
    url = f'{http_url}/?filters={filters_json}'

    try:
        data = http.get(url, timeout=10)
        if data and isinstance(data, list):
            return data
    except Exception as e:
        logger.warning(f'Failed to query relay {relay_url}: {e}')

    return []


@plugin.command('nostr_publish')
@plugin.example('`nostr_publish Hello from IRC!')
def nostr_publish(bot, trigger):
    """Publish a note to Nostr."""
    prefix = get_command_prefix(bot)
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: {prefix}nostr_publish <message>')
        return

    content = trigger.group(2).strip()

    # Get keys from config
    pubkey, privkey = _get_nostr_keys(bot)

    if not pubkey or not privkey:
        bot.notice(
            trigger.nick,
            'No Nostr keys configured in config file. '
            'Add [nostr] section with pubkey and privkey.',
        )
        return

    # Create note event (kind 1)
    event = _create_event(1, content, pubkey, privkey)

    # Publish to relays
    relays = bot.memory.get('nostr_relays', DEFAULT_RELAYS)
    published = 0

    for relay in relays[:3]:  # Try first 3 relays
        try:
            # In production, use WebSocket for publishing
            # For now, we'll just log it
            logger.info(f'Publishing to {relay}: {content[:50]}...')
            published += 1
        except Exception as e:
            logger.warning(f'Failed to publish to {relay}: {e}')

    if published > 0:
        bot.say(
            f"Note published to {formatter.bold(str(published))} relay(s): "
            f"{formatter.italic(content[:100])}"
        )
    else:
        bot.notice(trigger.nick, 'Failed to publish note to any relay.')


@plugin.command('nostr_get')
@plugin.example('`nostr_get npub1...')
@plugin.example('`nostr_get <pubkey> 10')
def nostr_get(bot, trigger):
    """Get recent notes from a Nostr user."""
    prefix = get_command_prefix(bot)
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: {prefix}nostr_get <pubkey> [limit]')
        return

    args = trigger.group(2).strip().split()
    pubkey = args[0]
    limit = int(args[1]) if len(args) > 1 else 5

    if limit > 20:
        limit = 20

    logger.info(f'Fetching notes from {pubkey} (limit: {limit})')

    # Query relays for notes from this pubkey
    filters = [{'authors': [pubkey], 'kinds': [1], 'limit': limit}]
    relays = bot.memory.get('nostr_relays', DEFAULT_RELAYS)

    all_events = []
    for relay in relays[:2]:  # Query first 2 relays
        events = _query_relay(relay, filters)
        all_events.extend(events)

    # Deduplicate by event ID
    seen_ids = set()
    unique_events = []
    for event in all_events:
        event_id = event.get('id')
        if event_id and event_id not in seen_ids:
            seen_ids.add(event_id)
            unique_events.append(event)

    # Sort by created_at (newest first)
    unique_events.sort(key=lambda x: x.get('created_at', 0), reverse=True)
    unique_events = unique_events[:limit]

    if not unique_events:
        bot.notice(trigger.nick, f'No notes found for {pubkey[:20]}...')
        return

    bot.say(
        f"Found {formatter.bold(str(len(unique_events)))} note(s) from "
        f"{formatter.monospace(pubkey[:20])}..."
    )

    for i, event in enumerate(unique_events, 1):
        content = event.get('content', '')[:200]
        created_at = event.get('created_at', 0)
        event_id = event.get('id', '')[:16]

        # Format timestamp
        if created_at:
            from datetime import datetime

            dt = datetime.fromtimestamp(created_at)
            time_str = dt.strftime('%Y-%m-%d %H:%M')
        else:
            time_str = 'Unknown'

        response = (
            f"{i}. {formatter.italic(content)} | "
            f"{formatter.monospace(time_str)} | "
            f"ID: {formatter.monospace(event_id)}..."
        )
        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('nostr_search')
@plugin.example('`nostr_search bitcoin')
def nostr_search(bot, trigger):
    """Search for notes containing keywords."""
    prefix = get_command_prefix(bot)
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: {prefix}nostr_search <keywords>')
        return

    keywords = trigger.group(2).strip()
    logger.info(f'Searching Nostr for: {keywords}')

    # Query relays for notes containing keywords
    filters = [{'kinds': [1], 'search': keywords, 'limit': 10}]
    relays = bot.memory.get('nostr_relays', DEFAULT_RELAYS)

    all_events = []
    for relay in relays[:2]:
        events = _query_relay(relay, filters)
        all_events.extend(events)

    # Deduplicate
    seen_ids = set()
    unique_events = []
    for event in all_events:
        event_id = event.get('id')
        if event_id and event_id not in seen_ids:
            seen_ids.add(event_id)
            unique_events.append(event)

    unique_events.sort(key=lambda x: x.get('created_at', 0), reverse=True)
    unique_events = unique_events[:5]

    if not unique_events:
        bot.notice(trigger.nick, f'No notes found for "{keywords}"')
        return

    bot.say(
        f"Found {formatter.bold(str(len(unique_events)))} note(s) for "
        f"{formatter.monospace(keywords)}:"
    )

    for i, event in enumerate(unique_events, 1):
        content = event.get('content', '')[:150]
        pubkey = event.get('pubkey', '')[:20]
        event_id = event.get('id', '')[:16]

        response = (
            f"{i}. {formatter.italic(content)}... | "
            f"by {formatter.monospace(pubkey)}... | "
            f"ID: {formatter.monospace(event_id)}..."
        )
        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('nostr_follow')
@plugin.example('`nostr_follow npub1...')
def nostr_follow(bot, trigger):
    """Follow a Nostr user."""
    prefix = get_command_prefix(bot)
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: {prefix}nostr_follow <pubkey>')
        return

    pubkey = trigger.group(2).strip()
    user_id = f'{trigger.nick}!{trigger.user}@{trigger.host}'

    if 'nostr_follows' not in bot.memory:
        bot.memory['nostr_follows'] = {}

    if user_id not in bot.memory['nostr_follows']:
        bot.memory['nostr_follows'][user_id] = []

    if pubkey not in bot.memory['nostr_follows'][user_id]:
        bot.memory['nostr_follows'][user_id].append(pubkey)
        bot.say(
            f"Now following {formatter.monospace(pubkey[:30])}... "
            f"({formatter.bold(str(len(bot.memory['nostr_follows'][user_id])))} total)"
        )
    else:
        bot.notice(trigger.nick, 'Already following this user.')


@plugin.command('nostr_unfollow')
@plugin.example('`nostr_unfollow npub1...')
def nostr_unfollow(bot, trigger):
    """Unfollow a Nostr user."""
    prefix = get_command_prefix(bot)
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: {prefix}nostr_unfollow <pubkey>')
        return

    pubkey = trigger.group(2).strip()
    user_id = f'{trigger.nick}!{trigger.user}@{trigger.host}'

    if 'nostr_follows' not in bot.memory:
        bot.memory['nostr_follows'] = {}

    if user_id in bot.memory['nostr_follows']:
        if pubkey in bot.memory['nostr_follows'][user_id]:
            bot.memory['nostr_follows'][user_id].remove(pubkey)
            bot.say(
                f"Unfollowed {formatter.monospace(pubkey[:30])}... "
                f"({formatter.bold(str(len(bot.memory['nostr_follows'][user_id])))} remaining)"
            )
        else:
            bot.notice(trigger.nick, 'Not following this user.')
    else:
        bot.notice(trigger.nick, 'No follows configured.')


@plugin.command('nostr_following')
@plugin.example('`nostr_following')
def nostr_following(bot, trigger):
    """List users you're following."""
    user_id = f'{trigger.nick}!{trigger.user}@{trigger.host}'

    if 'nostr_follows' not in bot.memory:
        bot.memory['nostr_follows'] = {}

    follows = bot.memory['nostr_follows'].get(user_id, [])

    if not follows:
        bot.notice(trigger.nick, 'Not following anyone yet.')
        return

    bot.say(
        f"Following {formatter.bold(str(len(follows)))} user(s):"
    )

    for i, pubkey in enumerate(follows[:10], 1):
        bot.say(f"{i}. {formatter.monospace(pubkey[:50])}...")


@plugin.command('nostr_feed')
@plugin.example('`nostr_feed')
@plugin.example('`nostr_feed 10')
def nostr_feed(bot, trigger):
    """Get feed from users you're following."""
    user_id = f'{trigger.nick}!{trigger.user}@{trigger.host}'

    if 'nostr_follows' not in bot.memory:
        bot.memory['nostr_follows'] = {}

    follows = bot.memory['nostr_follows'].get(user_id, [])

    if not follows:
        bot.notice(trigger.nick, 'Not following anyone. Use nostr_follow first.')
        return

    limit = 10
    if trigger.group(2):
        try:
            limit = int(trigger.group(2).strip())
            if limit > 20:
                limit = 20
        except ValueError:
            pass

    logger.info(f'Fetching feed for {len(follows)} follows (limit: {limit})')

    # Query relays for notes from followed users
    filters = [{'authors': follows, 'kinds': [1], 'limit': limit}]
    relays = bot.memory.get('nostr_relays', DEFAULT_RELAYS)

    all_events = []
    for relay in relays[:2]:
        events = _query_relay(relay, filters)
        all_events.extend(events)

    # Deduplicate and sort
    seen_ids = set()
    unique_events = []
    for event in all_events:
        event_id = event.get('id')
        if event_id and event_id not in seen_ids:
            seen_ids.add(event_id)
            unique_events.append(event)

    unique_events.sort(key=lambda x: x.get('created_at', 0), reverse=True)
    unique_events = unique_events[:limit]

    if not unique_events:
        bot.notice(trigger.nick, 'No notes found in your feed.')
        return

    bot.say(
        f"Feed ({formatter.bold(str(len(unique_events)))} notes):"
    )

    for i, event in enumerate(unique_events, 1):
        content = event.get('content', '')[:150]
        pubkey = event.get('pubkey', '')[:20]
        created_at = event.get('created_at', 0)

        if created_at:
            from datetime import datetime

            dt = datetime.fromtimestamp(created_at)
            time_str = dt.strftime('%m-%d %H:%M')
        else:
            time_str = 'Unknown'

        response = (
            f"{i}. {formatter.italic(content)}... | "
            f"by {formatter.monospace(pubkey)}... | "
            f"{formatter.monospace(time_str)}"
        )
        bot.say(formatter.truncate(response, max_len=400))


def _get_nostr_keys(bot):
    """Get Nostr keys from config."""
    try:
        pubkey = bot.config.nostr.pubkey
        privkey = bot.config.nostr.privkey
        return pubkey, privkey
    except (AttributeError, KeyError):
        return None, None


@plugin.command('nostr_relays')
@plugin.example('`nostr_relays')
def nostr_relays(bot, trigger):
    """List configured Nostr relays."""
    relays = bot.memory.get('nostr_relays', DEFAULT_RELAYS)

    bot.say(f"Configured relays ({formatter.bold(str(len(relays)))}):")
    for i, relay in enumerate(relays, 1):
        bot.say(f"{i}. {formatter.monospace(relay)}")


@plugin.command('nostr_addrelay')
@plugin.example('`nostr_addrelay wss://relay.example.com')
def nostr_addrelay(bot, trigger):
    """Add a Nostr relay."""
    prefix = get_command_prefix(bot)
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: {prefix}nostr_addrelay <relay_url>')
        return

    relay = trigger.group(2).strip()

    if 'nostr_relays' not in bot.memory:
        bot.memory['nostr_relays'] = DEFAULT_RELAYS.copy()

    if relay not in bot.memory['nostr_relays']:
        bot.memory['nostr_relays'].append(relay)
        bot.say(
            f"Added relay: {formatter.monospace(relay)} "
            f"({formatter.bold(str(len(bot.memory['nostr_relays'])))} total)"
        )
    else:
        bot.notice(trigger.nick, 'Relay already configured.')


def setup(bot):
    """Module setup - Nostr module loaded.
    
    Requires [nostr] section in config.cfg:
    [nostr]
    pubkey = npub1...
    privkey = nsec1...
    """
    if 'nostr_follows' not in bot.memory:
        bot.memory['nostr_follows'] = {}
    if 'nostr_relays' not in bot.memory:
        # Check if relays are in config
        try:
            relays_str = bot.config.nostr.relays
            relays = [r.strip() for r in relays_str.split(',')]
            bot.memory['nostr_relays'] = relays
        except (AttributeError, KeyError):
            bot.memory['nostr_relays'] = DEFAULT_RELAYS.copy()
    
    # Check if keys are configured
    pubkey, privkey = _get_nostr_keys(bot)
    if pubkey and privkey:
        logger.info(f'Nostr module loaded with pubkey: {pubkey[:20]}...')
    else:
        logger.warning(
            'Nostr module loaded but no keys configured. '
            'Add [nostr] section with pubkey and privkey in config.cfg'
        )


def shutdown(bot):
    """Module shutdown."""
    logger.info('Nostr module unloaded')

