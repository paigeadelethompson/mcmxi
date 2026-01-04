"""
Sopel module to query Jitsi Meet instances from a configured list.
"""
from sopel import plugin
import requests
import random
import threading
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get_module_logger, IRCFormatter
from http_client import HTTPClient

logger = get_module_logger(__name__)
formatter = IRCFormatter()
http_client = HTTPClient()

# Load Jitsi instances from config.cfg
_jitsi_instances = []
_jitsi_loaded = False

def _load_jitsi_instances(bot):
    global _jitsi_instances, _jitsi_loaded
    if _jitsi_loaded:
        return
    try:
        # Look for [jitsi] section in config
        if hasattr(bot.config, 'jitsi'):
            section = bot.config.jitsi
            if hasattr(section, 'instances'):
                if isinstance(section.instances, str):
                    _jitsi_instances = [x.strip() for x in section.instances.split(',') if x.strip()]
                elif isinstance(section.instances, list):
                    _jitsi_instances = [x.strip() for x in section.instances if x.strip()]
        _jitsi_loaded = True
    except Exception as e:
        logger.error(f'Could not load Jitsi instances from config: {e}')
        _jitsi_loaded = True

def _get_jitsi_instances(bot):
    _load_jitsi_instances(bot)
    return _jitsi_instances

@plugin.command('jitsi')
@plugin.example('`jitsi')
@plugin.example('`jitsi meet.example.com')
@plugin.example('`jitsi meet.example.com roomname')
def jitsi_query(bot, trigger):
    """Query a Jitsi instance for status, or info about a room, or pick a random one from config."""
    prefix = getattr(bot.config.core, 'prefix', '`')
    instances = _get_jitsi_instances(bot)
    if not instances:
        bot.say('No Jitsi instances configured. Please add a [jitsi] section with instances=... in config.cfg')
        return
    args = trigger.group(2).strip().split() if trigger.group(2) else []
    if args:
        instance = args[0]
        if instance not in instances:
            bot.say(f'Instance {instance} not in configured list.')
            return
        room = args[1] if len(args) > 1 else None
    else:
        instance = random.choice(instances)
        room = None
    if not room:
        url = f'https://{instance}/about/health'
        resp = http_client.get(url)
        if resp and (resp.get('status') == 'ok' or 'text' in resp):
            bot.say(f'Jitsi instance {instance} is UP.')
        elif resp:
            bot.say(f'Jitsi instance {instance} returned: {resp}')
        else:
            bot.say(f'Could not reach Jitsi instance {instance}.')
    else:
        # Try to get info about the room (if supported)
        about_rooms_url = f'https://{instance}/about/rooms'
        resp = http_client.get(about_rooms_url)
        if resp and isinstance(resp, dict) and 'rooms' in resp:
            rooms = resp.get('rooms', [])
            found = next((r for r in rooms if r.get('id') == room or r.get('name') == room), None)
            if found:
                bot.say(f"Room '{room}' exists on {instance}. Info: {found}")
            else:
                bot.say(f"Room '{room}' not found on {instance} (via /about/rooms).")
            return
        # Try /colibri/stats
        colibri_url = f'https://{instance}/colibri/stats'
        resp = http_client.get(colibri_url)
        if resp and isinstance(resp, dict) and 'conferences' in resp:
            confs = resp.get('conferences', [])
            found = [c for c in confs if room in str(c)]
            if found:
                bot.say(f"Room '{room}' is active on {instance} (colibri/stats): {found}")
                return
        # Fallback: provide a join link
        bot.say(f"Room info not available via API. Join link: https://{instance}/{room}")

@plugin.command('jitsi_rooms')
@plugin.example('`jitsi_rooms')
@plugin.example('`jitsi_rooms meet.example.com')
def jitsi_rooms(bot, trigger):
    """List available rooms on a Jitsi instance (if supported by /about/rooms)."""
    instances = _get_jitsi_instances(bot)
    if not instances:
        bot.say('No Jitsi instances configured. Please add a [jitsi] section with instances=... in config.cfg')
        return
    args = trigger.group(2).strip().split() if trigger.group(2) else []
    if args:
        instance = args[0]
        if instance not in instances:
            bot.say(f'Instance {instance} not in configured list.')
            return
    else:
        instance = random.choice(instances)
    about_rooms_url = f'https://{instance}/about/rooms'
    resp = http_client.get(about_rooms_url)
    if resp and isinstance(resp, dict) and 'rooms' in resp:
        rooms = resp.get('rooms', [])
        if not rooms:
            bot.say(f'No rooms found on {instance} (via /about/rooms).')
            return
        bot.say(f"Rooms on {instance}:")
        for r in rooms[:10]:
            name = r.get('name') or r.get('id')
            bot.say(f"- {name}")
        if len(rooms) > 10:
            bot.say(f"...and {len(rooms)-10} more. (Only first 10 shown)")
    else:
        bot.say(f'/about/rooms not available or not JSON on {instance}.')
