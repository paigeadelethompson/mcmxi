"""
Sopel module for Meshtastic public MQTT server integration.
Connects to mqtt.meshtastic.org to monitor mesh network traffic.
"""
import json
import os
import sys
import threading
import time
import uuid
from collections import defaultdict
from typing import Dict, List, Optional

import paho.mqtt.client as mqtt
from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import IRCFormatter, get_module_logger, get_command_prefix, get_command_prefix

logger = get_module_logger(__name__)
formatter = IRCFormatter()

# Default Meshtastic public MQTT broker
DEFAULT_BROKER = 'mqtt.meshtastic.org'
DEFAULT_PORT = 1883
# Default credentials for public server (per documentation)
DEFAULT_USERNAME = 'meshdev'
DEFAULT_PASSWORD = 'large4cats'

# Meshtastic regions
REGIONS = {
    'US': 'United States',
    'EU': 'Europe',
    'CN': 'China',
    'JP': 'Japan',
    'ANZ': 'Australia/New Zealand',
    'KR': 'Korea',
    'TW': 'Taiwan',
    'RU': 'Russia',
    'PH': 'Philippines',
    'MY': 'Malaysia',
    'IN': 'India',
    'IL': 'Israel',
    'GB': 'United Kingdom',
    'CA': 'Canada',
    'MX': 'Mexico',
    'BR': 'Brazil',
    'AR': 'Argentina',
    'AU': 'Australia',
    'NZ': 'New Zealand',
    'ZA': 'South Africa',
}

# Node data cache - keyed by decimal node ID
node_cache: Dict[int, Dict] = {}
cache_lock = threading.Lock()

# Message cache for recent messages
message_cache: List[Dict] = []
message_cache_lock = threading.Lock()
MAX_MESSAGE_CACHE = 1000

# Global MQTT client
mqtt_client: Optional[mqtt.Client] = None
mqtt_lock = threading.Lock()
mqtt_connected = False
active_subscriptions: set = set()

# Channel subscriptions: {channel: [regions]}
channel_subscriptions: Dict[str, List[str]] = defaultdict(list)
channel_lock = threading.Lock()

# Channel message filters: {channel: {'include': set, 'exclude': set}}
# If include is empty, all types are included (unless excluded)
channel_filters: Dict[str, Dict[str, set]] = defaultdict(
    lambda: {'include': set(), 'exclude': set()}
)
filter_lock = threading.Lock()

# Bot instance for sending messages
bot_instance = None

# Available message types
MESSAGE_TYPES = {'nodeinfo', 'position', 'telemetry', 'text', 'textmessage'}


def _on_connect(client, userdata, flags, rc):
    """Handle MQTT connection."""
    global mqtt_connected
    
    # MQTT return codes
    rc_messages = {
        0: 'Connection successful',
        1: 'Connection refused - incorrect protocol version',
        2: 'Connection refused - invalid client identifier',
        3: 'Connection refused - server unavailable',
        4: 'Connection refused - bad username or password',
        5: 'Connection refused - not authorized'
    }
    
    if rc == 0:
        mqtt_connected = True
        logger.info(f'Connected to Meshtastic MQTT broker {DEFAULT_BROKER}')
    else:
        mqtt_connected = False
        msg = rc_messages.get(rc, f'Unknown error code {rc}')
        logger.error(f'Failed to connect to MQTT broker: {rc} - {msg}')


def _on_message(client, userdata, msg):
    """Handle incoming MQTT messages from public broker."""
    try:
        topic = msg.topic
        payload = msg.payload

        # Parse topic: msh/REGION/2/json/CHANNELNAME/USERID
        parts = topic.split('/')
        if (len(parts) < 6 or parts[0] != 'msh' or
                parts[2] != '2' or parts[3] != 'json'):
            return

        region = parts[1]
        channel = parts[4]
        user_id_hex = parts[5] if len(parts) > 5 else None

        # Try to parse as JSON
        try:
            data = json.loads(payload.decode('utf-8'))
            _process_json_message(topic, region, channel, user_id_hex, data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Not JSON, might be protobuf - ignore for now
            logger.debug(f'Received non-JSON message on {topic}')

    except Exception as e:
        logger.error(f'Error processing MQTT message: {e}')


def _should_send_message(channel: str, msg_type: str) -> bool:
    """Check if message type should be sent to channel based on filters."""
    with filter_lock:
        filters = channel_filters.get(channel, {'include': set(), 'exclude': set()})
        include = filters.get('include', set())
        exclude = filters.get('exclude', set())
        
        # Normalize message type
        msg_type_lower = msg_type.lower()
        if msg_type_lower == 'textmessage':
            msg_type_lower = 'text'
        
        # If excluded, don't send
        if msg_type_lower in exclude or msg_type in exclude:
            return False
        
        # If include list is empty, send all (unless excluded above)
        if not include:
            return True
        
        # If include list has items, only send if in include list
        return msg_type_lower in include or msg_type in include


def _send_to_channels(region: str, message: str, msg_type: str = 'text'):
    """Send message to all channels subscribed to this region."""
    global bot_instance
    if not bot_instance:
        return

    with channel_lock:
        for irc_channel, subscribed_regions in channel_subscriptions.items():
            if region.upper() in [r.upper() for r in subscribed_regions]:
                # Check if message type should be sent
                if not _should_send_message(irc_channel, msg_type):
                    continue
                
                try:
                    # bot.say() is thread-safe in Sopel
                    bot_instance.say(message, irc_channel)
                except Exception as e:
                    logger.error(f'Error sending to channel {irc_channel}: {e}')


def _process_json_message(
    topic: str, region: str, channel: str,
    user_id_hex: Optional[str], data: Dict
):
    """Process JSON message and update node cache."""
    try:
        # Get node ID from message (decimal format)
        node_id_dec = data.get('from')
        if not node_id_dec:
            return

        # Convert to hex if needed
        if user_id_hex and user_id_hex.startswith('!'):
            node_id_hex = user_id_hex
        else:
            node_id_hex = f'!{node_id_dec:08x}'

        # Update node cache
        with cache_lock:
            if node_id_dec not in node_cache:
                node_cache[node_id_dec] = {
                    'node_id_hex': node_id_hex,
                    'node_id_dec': node_id_dec,
                    'region': region,
                    'last_seen': time.time(),
                    'messages': []
                }

            node = node_cache[node_id_dec]
            node['last_seen'] = time.time()
            node['region'] = region

            # Process by message type
            msg_type = data.get('type', '')
            payload = data.get('payload', {})

            if msg_type == 'nodeinfo':
                node['longname'] = payload.get('longname', '')
                node['shortname'] = payload.get('shortname', '')
                node['hardware'] = payload.get('hardware', '')
                node['id'] = payload.get('id', node_id_hex)
                # Optionally send nodeinfo updates to channels
                shortname = node.get('shortname', 'N/A')
                longname = node.get('longname', '')
                hardware = payload.get('hardware', '')
                
                # Hardware type mapping (common values)
                hardware_map = {
                    0: 'UNSET',
                    1: 'TLORA_V2',
                    2: 'TLORA_V1',
                    3: 'TLORA_V2_1_1p6',
                    4: 'TBEAM',
                    5: 'HELTEC_V2_0',
                    6: 'TBEAM_V0P7',
                    7: 'T_ECHO',
                    8: 'TLORA_V1_1p3',
                    9: 'RAK4631',
                    10: 'HELTEC_V2_1',
                    11: 'HELTEC_V3',
                    12: 'HELTEC_WSL_V3',
                    13: 'BETAFPV_2400_TX',
                    14: 'BETAFPV_900_TX',
                    15: 'RPI_PICO',
                    16: 'HELTEC_WIRELESS_TRACKER',
                    17: 'HELTEC_WIRELESS_PAPER',
                    18: 'T_DECK',
                    19: 'T_WATCH_S3',
                    20: 'PICOMPUTER_S3',
                    21: 'HELTEC_HT62',
                    22: 'HELTEC_V3_EXT',
                    23: 'HELTEC_WSL_LORA_V3',
                    24: 'HELTEC_WSL_LORA_V3_EXT',
                }
                if hardware:
                    hardware_name = hardware_map.get(
                        hardware, f'HW{hardware}'
                    )
                else:
                    hardware_name = 'Unknown'
                
                parts = []
                if longname:
                    parts.append(
                        f"{formatter.bold('Long')}: {formatter.monospace(longname)}"
                    )
                if shortname and shortname != 'N/A':
                    parts.append(
                        f"{formatter.bold('Short')}: {formatter.monospace(shortname)}"
                    )
                if hardware_name:
                    parts.append(
                        f"{formatter.bold('HW')}: {formatter.monospace(hardware_name)}"
                    )
                
                info_str = ' | '.join(parts) if parts else 'Node info'
                irc_msg = (
                    f"[{formatter.bold(region)}] {formatter.monospace(node_id_hex)}: "
                    f"{info_str}"
                )
                _send_to_channels(region, irc_msg, 'nodeinfo')
            elif msg_type == 'position':
                # Position uses latitude_i and longitude_i (integer * 1e7)
                lat_i = payload.get('latitude_i', 0)
                lon_i = payload.get('longitude_i', 0)
                node['latitude'] = lat_i / 1e7 if lat_i else None
                node['longitude'] = lon_i / 1e7 if lon_i else None
                node['altitude'] = payload.get('altitude', 0)
                node['time'] = payload.get('time', 0)
                # Optionally send position updates to channels
                if node['latitude'] is not None and node['longitude'] is not None:
                    shortname = node.get('shortname', node_id_hex)
                    lat = node['latitude']
                    lon = node['longitude']
                    irc_msg = (
                        f"[{formatter.bold(region)}] "
                        f"{formatter.monospace(shortname)} "
                        f"({formatter.monospace(node_id_hex)}): "
                        f"{formatter.bold('Position')} {lat:.4f}, {lon:.4f}"
                    )
                    _send_to_channels(region, irc_msg, 'position')
            elif msg_type == 'telemetry':
                node['telemetry'] = payload
                # Optionally send telemetry updates to channels
                shortname = node.get('shortname', node_id_hex)
                irc_msg = (
                    f"[{formatter.bold(region)}] "
                    f"{formatter.monospace(shortname)} "
                    f"({formatter.monospace(node_id_hex)}): "
                    f"{formatter.bold('Telemetry')} update"
                )
                _send_to_channels(region, irc_msg, 'telemetry')
            elif msg_type in ('text', 'textmessage'):
                # Store text messages
                text = payload if isinstance(payload, str) else payload.get('text', '')
                if text:
                    msg_entry = {
                        'type': 'text',
                        'text': text,
                        'timestamp': data.get('timestamp', time.time()),
                        'channel': channel,
                        'id': data.get('id')
                    }
                    node['messages'].append(msg_entry)
                    # Keep only last 50 messages per node
                    if len(node['messages']) > 50:
                        node['messages'] = node['messages'][-50:]
                    
                    # Send to IRC channels listening to this region
                    shortname = node.get('shortname', node_id_hex)
                    irc_msg = (
                        f"[{formatter.bold(region)}] "
                        f"{formatter.monospace(shortname)} "
                        f"({formatter.monospace(node_id_hex)}): {text[:300]}"
                    )
                    _send_to_channels(region, irc_msg, 'text')

        # Add to message cache
        with message_cache_lock:
            msg_entry = {
                'topic': topic,
                'region': region,
                'channel': channel,
                'node_id_hex': node_id_hex,
                'node_id_dec': node_id_dec,
                'type': msg_type,
                'data': data,
                'timestamp': time.time()
            }
            message_cache.append(msg_entry)
            # Keep only recent messages
            if len(message_cache) > MAX_MESSAGE_CACHE:
                message_cache.pop(0)

    except Exception as e:
        logger.error(f'Error processing JSON message: {e}')


def ensure_mqtt_connected() -> bool:
    """Ensure MQTT client is connected."""
    global mqtt_client, mqtt_connected

    with mqtt_lock:
        if mqtt_client and mqtt_connected:
            return True

        # Clean up old client if exists
        if mqtt_client:
            try:
                mqtt_client.loop_stop()
                mqtt_client.disconnect()
            except Exception:
                pass
            mqtt_client = None
            mqtt_connected = False

        try:
            # Generate unique client ID (required by some brokers)
            client_id = f'sopel-meshtastic-{uuid.uuid4().hex[:8]}'
            
            mqtt_client = mqtt.Client(
                client_id=client_id,
                clean_session=True,
                protocol=mqtt.MQTTv311
            )
            mqtt_client.on_connect = _on_connect
            mqtt_client.on_message = _on_message

            # Set default credentials for public server
            # Per docs: https://meshtastic.org/docs/configuration/module/mqtt/
            mqtt_client.username_pw_set(
                username=DEFAULT_USERNAME,
                password=DEFAULT_PASSWORD
            )

            # Connect to public broker (no auth needed)
            logger.info(f'Connecting to {DEFAULT_BROKER}:{DEFAULT_PORT}...')
            try:
                mqtt_client.connect(DEFAULT_BROKER, DEFAULT_PORT, keepalive=60)
            except Exception as conn_err:
                logger.error(f'Connection error: {conn_err}')
                mqtt_client = None
                return False
            
            mqtt_client.loop_start()

            # Wait for connection
            for _ in range(100):  # 10 seconds max
                if mqtt_connected:
                    logger.info('Successfully connected to MQTT broker')
                    return True
                time.sleep(0.1)

            # If connection failed, log the error
            if not mqtt_connected:
                logger.error(
                    f'Failed to connect to MQTT broker after timeout. '
                    f'Check if {DEFAULT_BROKER}:{DEFAULT_PORT} is accessible.'
                )
            return False
        except Exception as e:
            logger.error(f'Error connecting to MQTT: {e}')
            return False


def subscribe_region(region: str) -> bool:
    """Subscribe to all JSON topics for a region."""
    if not ensure_mqtt_connected():
        return False

    # Subscribe to: msh/REGION/2/json/+/+
    # This gets all channels and all nodes
    topic = f'msh/{region}/2/json/+/+'

    with mqtt_lock:
        if topic not in active_subscriptions:
            try:
                result = mqtt_client.subscribe(topic)
                if result[0] == mqtt.MQTT_ERR_SUCCESS:
                    active_subscriptions.add(topic)
                    logger.info(f'Subscribed to {topic}')
                    return True
            except Exception as e:
                logger.error(f'Error subscribing to {topic}: {e}')

    return topic in active_subscriptions


def publish_message(region: str, node_id_dec: int, message_type: str,
                    payload: Dict, to_node: Optional[int] = None,
                    channel: int = 0) -> bool:
    """Publish message to MQTT downlink topic."""
    if not ensure_mqtt_connected():
        return False

    # Topic for downlink: msh/REGION/2/json/mqtt/
    topic = f'msh/{region}/2/json/mqtt/'

    # Build message according to docs
    msg = {
        'from': node_id_dec,
        'type': message_type,
        'payload': payload
    }

    if to_node is not None:
        msg['to'] = to_node

    if channel != 0:
        msg['channel'] = channel

    try:
        result = mqtt_client.publish(topic, json.dumps(msg))
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    except Exception as e:
        logger.error(f'Error publishing message: {e}')
        return False


@plugin.command('mesh_regions')
@plugin.example('`mesh_regions')
def mesh_regions(bot, trigger):
    """List available Meshtastic regions."""
    bot.say(f"{formatter.bold('Available Meshtastic Regions')}:")
    for code, name in sorted(REGIONS.items()):
        bot.say(f"{code}: {name}")


@plugin.command('mesh_listen')
@plugin.example('`mesh_listen US')
@plugin.example('`mesh_listen EU')
def mesh_listen(bot, trigger):
    """Start listening to a region's MQTT traffic and route messages to this channel."""  # noqa: E501
    global bot_instance
    prefix = get_command_prefix(bot)
    
    # Store bot instance for sending messages from MQTT thread
    bot_instance = bot
    
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: {prefix}mesh_listen <region>')
        bot.notice(trigger.nick, f'Example: {prefix}mesh_listen US')
        return

    region = trigger.group(2).strip().upper()

    if region not in REGIONS:
        bot.notice(trigger.nick, f'Unknown region: {region}')
        return

    # Get channel name
    channel = trigger.sender
    if not channel:
        bot.notice(trigger.nick, 'This command must be used in a channel')
        return

    # Subscribe channel to region
    with channel_lock:
        if region not in channel_subscriptions[channel]:
            channel_subscriptions[channel].append(region)

    bot.say(
        f"Subscribing to {formatter.bold(REGIONS[region])} ({region}) MQTT topics..."
    )

    if subscribe_region(region):
        bot.say(
            f"Now listening to {region}. Messages will be sent to this channel."
        )
        prefix = get_command_prefix(bot)
        bot.notice(
            trigger.nick,
            f"Use {prefix}mesh_nodes to see discovered nodes, "
            f"{prefix}mesh_messages to see recent messages"
        )
    else:
        bot.notice(trigger.nick, 'Failed to subscribe. Check MQTT connection.')


@plugin.command('mesh_stop')
@plugin.example('`mesh_stop US')
@plugin.example('`mesh_stop')
def mesh_stop(bot, trigger):
    """Stop listening to a region's MQTT traffic in this channel."""
    channel = trigger.sender
    if not channel:
        bot.notice(trigger.nick, 'This command must be used in a channel')
        return

    if trigger.group(2):
        # Stop specific region
        region = trigger.group(2).strip().upper()
        if region not in REGIONS:
            bot.notice(trigger.nick, f'Unknown region: {region}')
            return

        with channel_lock:
            if channel in channel_subscriptions:
                if region in channel_subscriptions[channel]:
                    channel_subscriptions[channel].remove(region)
                    if not channel_subscriptions[channel]:
                        del channel_subscriptions[channel]
                    bot.say(
                        f"Stopped listening to {formatter.bold(REGIONS[region])} "
                        f"({region}) in this channel"
                    )
                else:
                    bot.notice(
                        trigger.nick,
                        f'This channel is not listening to {region}'
                    )
            else:
                bot.notice(
                    trigger.nick,
                    'This channel is not listening to any regions'
                )
    else:
        # Stop all regions for this channel
        with channel_lock:
            if channel in channel_subscriptions:
                regions = channel_subscriptions[channel].copy()
                del channel_subscriptions[channel]
                if regions:
                    region_list = ', '.join(regions)
                    bot.say(
                        f"Stopped listening to all regions ({region_list}) "
                        f"in this channel"
                    )
                else:
                    bot.say(
                        "Stopped listening to all regions in this channel"
                    )
            else:
                bot.notice(
                    trigger.nick,
                    'This channel is not listening to any regions'
                )


@plugin.command('mesh_filter')
@plugin.example('`mesh_filter')
@plugin.example('`mesh_filter +text -telemetry -position')
@plugin.example('`mesh_filter -telemetry -position +text')
def mesh_filter(bot, trigger):
    """Set message type filters for this channel."""
    channel = trigger.sender
    if not channel:
        bot.notice(trigger.nick, 'This command must be used in a channel')
        return

    with filter_lock:
        filters = channel_filters[channel]
        include = filters['include']
        exclude = filters['exclude']

        if not trigger.group(2):
            # Show current filters
            if not include and not exclude:
                bot.say('No filters set - all message types are enabled')
            else:
                if include:
                    bot.say(f"Include: {', '.join(sorted(include))}")
                if exclude:
                    bot.say(f"Exclude: {', '.join(sorted(exclude))}")
            bot.say(f"Available types: {', '.join(sorted(MESSAGE_TYPES))}")
            bot.say(
                'Usage: `mesh_filter +type1 -type2 '
                '(use + to include, - to exclude)'
            )
            return

        # Parse filter arguments
        args = trigger.group(2).strip().split()
        new_include = set()
        new_exclude = set()

        for arg in args:
            if arg.startswith('+'):
                msg_type = arg[1:].lower()
                if msg_type == 'textmessage':
                    msg_type = 'text'
                if msg_type in MESSAGE_TYPES or msg_type == 'text':
                    new_include.add(msg_type)
                    # Remove from exclude if it was there
                    exclude.discard(msg_type)
                    exclude.discard('textmessage')
                else:
                    bot.notice(trigger.nick, f'Unknown message type: {arg[1:]}')
            elif arg.startswith('-'):
                msg_type = arg[1:].lower()
                if msg_type == 'textmessage':
                    msg_type = 'text'
                if msg_type in MESSAGE_TYPES or msg_type == 'text':
                    new_exclude.add(msg_type)
                    # Remove from include if it was there
                    include.discard(msg_type)
                    include.discard('textmessage')
                else:
                    bot.notice(trigger.nick, f'Unknown message type: {arg[1:]}')
            else:
                bot.notice(
                    trigger.nick,
                    f'Invalid filter: {arg} (use + or - prefix)'
                )

        # Update filters
        if new_include:
            include.update(new_include)
        if new_exclude:
            exclude.update(new_exclude)

        # Show updated filters
        if include:
            bot.say(f"Include: {', '.join(sorted(include))}")
        if exclude:
            bot.say(f"Exclude: {', '.join(sorted(exclude))}")
        if not include and not exclude:
            bot.say('All filters cleared - all message types enabled')


@plugin.command('mesh_nodes')
@plugin.example('`mesh_nodes')
@plugin.example('`mesh_nodes US')
@plugin.example('`mesh_nodes US @last_seen/desc')
@plugin.example('`mesh_nodes US @shortname/asc page 2')
def mesh_nodes(bot, trigger):
    """List nodes discovered from MQTT traffic."""
    prefix = get_command_prefix(bot)
    # Parse arguments
    args = trigger.group(2).strip().split() if trigger.group(2) else []
    
    region_filter = None
    sort_col = 'last_seen'
    sort_dir = 'desc'
    page = 1
    page_size = 20
    
    # Available sort columns
    sort_columns = {
        'node_id': 'node_id_hex',
        'shortname': 'shortname',
        'short': 'shortname',
        'longname': 'longname',
        'long': 'longname',
        'region': 'region',
        'last_seen': 'last_seen',
        'seen': 'last_seen'
    }
    
    i = 0
    while i < len(args):
        arg = args[i].upper()
        
        # Check for region
        if arg in REGIONS:
            region_filter = arg
        # Check for sort (@col or @col/dir)
        elif arg.startswith('@'):
            sort_spec = arg[1:].lower()
            if '/' in sort_spec:
                parts = sort_spec.split('/', 1)
                sort_col = parts[0]
                sort_dir = parts[1]
            else:
                sort_col = sort_spec
                sort_dir = 'desc'  # default
            # Map to actual column name
            sort_col = sort_columns.get(sort_col, sort_col)
        # Check for page
        elif arg == 'PAGE' and i + 1 < len(args):
            try:
                page = int(args[i + 1])
                if page < 1:
                    page = 1
                i += 1
            except ValueError:
                bot.notice(trigger.nick, f'Invalid page number: {args[i + 1]}')
        i += 1
    
    # If no region specified but first arg looks like region, use it
    if not region_filter and args and args[0].upper() in REGIONS:
        region_filter = args[0].upper()

    with cache_lock:
        nodes = list(node_cache.values())
        if region_filter:
            nodes = [
                n for n in nodes
                if n.get('region', '').upper() == region_filter
            ]

    if not nodes:
        if region_filter:
            bot.say(f'No nodes found for region {region_filter}')
        else:
            bot.say(
                f'No nodes in cache. Use {prefix}mesh_listen <region> to start monitoring'
            )
        return

    # Sort nodes
    reverse = sort_dir.lower() == 'desc'
    
    def sort_key(node):
        value = node.get(sort_col, '')
        # Handle special cases
        if sort_col == 'last_seen':
            return value or 0
        elif sort_col == 'node_id_hex':
            # Sort hex IDs numerically
            try:
                return int(value[1:], 16) if value.startswith('!') else 0
            except (ValueError, AttributeError):
                return 0
        # String sort
        return str(value).lower() if value else ''
    
    nodes.sort(key=sort_key, reverse=reverse)

    # Pagination
    total_nodes = len(nodes)
    total_pages = (total_nodes + page_size - 1) // page_size
    if page > total_pages:
        page = total_pages
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_nodes = nodes[start_idx:end_idx]

    # Display header
    if region_filter:
        header = f"Nodes in {formatter.bold(REGIONS[region_filter])} ({region_filter})"
    else:
        header = f"{formatter.bold('All Discovered Nodes')}"
    
    if total_pages > 1:
        header += f" - Page {page}/{total_pages}"
    
    bot.say(header)
    
    if sort_col != 'last_seen' or sort_dir != 'desc':
        bot.say(f"Sorted by: {sort_col} ({sort_dir})")

    table_data = []
    for node in page_nodes:
        node_id = node.get('node_id_hex', 'N/A')
        shortname = node.get('shortname', 'N/A')
        longname = node.get('longname', '')
        region = node.get('region', 'N/A')
        last_seen = node.get('last_seen', 0)
        if last_seen:
            age = int(time.time() - last_seen)
            if age < 60:
                age_str = f'{age}s'
            elif age < 3600:
                age_str = f'{age//60}m'
            else:
                age_str = f'{age//3600}h'
        else:
            age_str = 'N/A'

        table_data.append([
            node_id,
            shortname,
            longname[:20] if longname else 'N/A',
            region,
            age_str
        ])

    if table_data:
        table_output = formatter.table(
            table_data,
            headers=['Node ID', 'Short', 'Long Name', 'Region', 'Last Seen']
        )
        for line in table_output.split('\n'):
            bot.say(line)

    # Show pagination info
    if total_pages > 1:
        bot.say(
            f"Showing {start_idx + 1}-{min(end_idx, total_nodes)} of {total_nodes} nodes. "
            f"Use 'page N' to navigate."
        )
    elif len(nodes) > page_size:
        bot.say(f"Showing {page_size} of {total_nodes} nodes. Use 'page N' to see more.")


@plugin.command('mesh_node')
@plugin.example('`mesh_node !7efeee00')
@plugin.example('`mesh_node 2130636288')
def mesh_node(bot, trigger):
    """Get detailed information about a Meshtastic node."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `mesh_node <node_id>')
        return

    node_id_str = trigger.group(2).strip()

    # Parse node ID
    if node_id_str.startswith('!'):
        try:
            node_id_dec = int(node_id_str[1:], 16)
        except ValueError:
            bot.notice(trigger.nick, 'Invalid hex node ID format')
            return
    elif node_id_str.isdigit():
        node_id_dec = int(node_id_str)
    else:
        bot.notice(trigger.nick, 'Invalid node ID format')
        return

    with cache_lock:
        node = node_cache.get(node_id_dec)

    if not node:
        bot.notice(trigger.nick, 'Node not found in cache')
        bot.notice(trigger.nick, f'Use {prefix}mesh_listen <region> to start monitoring')
        return

    # Display node info
    bot.say(f"{formatter.bold('Node Information')}:")
    bot.say(f"Node ID: {node.get('node_id_hex', 'N/A')} ({node_id_dec})")

    if node.get('longname'):
        bot.say(f"Long Name: {node.get('longname')}")
    if node.get('shortname'):
        bot.say(f"Short Name: {node.get('shortname')}")
    if node.get('region'):
        bot.say(f"Region: {node.get('region')}")
    if node.get('hardware'):
        bot.say(f"Hardware: {node.get('hardware')}")

    # Position
    if node.get('latitude') is not None and node.get('longitude') is not None:
        lat = node['latitude']
        lon = node['longitude']
        alt = node.get('altitude', 0)
        bot.say(f"Position: {lat:.6f}, {lon:.6f} (alt: {alt}m)")
        bot.say(f"Map: https://www.google.com/maps?q={lat},{lon}")

    # Telemetry
    if 'telemetry' in node:
        telemetry = node['telemetry']
        bot.say(f"{formatter.bold('Telemetry')}:")
        for key, value in list(telemetry.items())[:10]:
            bot.say(f"  {key}: {value}")

    # Recent messages
    messages = node.get('messages', [])
    if messages:
        bot.say(f"{formatter.bold('Recent Messages')} ({len(messages)}):")
        for msg in messages[-5:]:
            text = msg.get('text', '')[:100]
            bot.say(f"  {text}")

    # Last seen
    last_seen = node.get('last_seen', 0)
    if last_seen:
        age = int(time.time() - last_seen)
        bot.say(f"Last Seen: {age} seconds ago")


@plugin.command('mesh_messages')
@plugin.example('`mesh_messages')
@plugin.example('`mesh_messages 10')
def mesh_messages(bot, trigger):
    """Show recent messages from MQTT traffic."""
    count = 10
    if trigger.group(2):
        try:
            count = int(trigger.group(2).strip())
            count = min(count, 50)  # Limit to 50
        except ValueError:
            pass

    with message_cache_lock:
        if len(message_cache) > count:
            messages = message_cache[-count:]
        else:
            messages = message_cache

    if not messages:
        bot.say(
            f'No messages in cache. Use {prefix}mesh_listen <region> to start monitoring'
        )
        return

    bot.say(f"{formatter.bold('Recent Messages')} (last {len(messages)}):")

    for msg in messages:
        node_id = msg.get('node_id_hex', 'N/A')
        msg_type = msg.get('type', 'unknown')
        region = msg.get('region', 'N/A')
        data = msg.get('data', {})

        if msg_type == 'text' or msg_type == 'textmessage':
            payload = data.get('payload', {})
            text = payload if isinstance(payload, str) else payload.get('text', '')
            if text:
                bot.say(f"[{region}] {node_id} ({msg_type}): {text[:200]}")
        elif msg_type == 'nodeinfo':
            payload = data.get('payload', {})
            name = payload.get('longname') or payload.get('shortname', 'Unknown')
            bot.say(f"[{region}] {node_id} ({msg_type}): {name}")
        elif msg_type == 'position':
            payload = data.get('payload', {})
            lat_i = payload.get('latitude_i', 0)
            lon_i = payload.get('longitude_i', 0)
            if lat_i and lon_i:
                lat = lat_i / 1e7
                lon = lon_i / 1e7
                bot.say(
                    f"[{region}] {node_id} ({msg_type}): {lat:.6f}, {lon:.6f}"
                )
        else:
            bot.say(f"[{region}] {node_id} ({msg_type})")


@plugin.command('mesh_send')
@plugin.example('`mesh_send US 2130636288 "Hello from IRC"')
def mesh_send(bot, trigger):
    """Send a text message via MQTT downlink."""
    if not trigger.group(2):
        bot.notice(
            trigger.nick,
            'Usage: `mesh_send <region> <node_id_dec> "<message>"'
        )
        bot.notice(
            trigger.nick,
            'Note: Target node must have "mqtt" channel with downlink enabled'
        )
        return

    parts = trigger.group(2).strip().split(None, 2)
    if len(parts) < 3:
        bot.notice(
            trigger.nick,
            'Usage: `mesh_send <region> <node_id_dec> "<message>"'
        )
        return

    region = parts[0].upper()
    node_id_str = parts[1]
    message = parts[2].strip().strip('"').strip("'")

    if region not in REGIONS:
        bot.notice(trigger.nick, f'Unknown region: {region}')
        return

    # Parse node ID (decimal)
    try:
        node_id_dec = int(node_id_str)
    except ValueError:
        bot.notice(trigger.nick, 'Node ID must be decimal format (e.g., 2130636288)')
        return

    bot.say(f"Sending message via MQTT to {node_id_dec} in {region}...")

    success = publish_message(
        region, node_id_dec, 'sendtext', message
    )

    if success:
        bot.say("Message published to mqtt downlink topic")
        bot.say(
            "Note: Message will only be delivered if target has 'mqtt' channel enabled"
        )
    else:
        bot.notice(trigger.nick, 'Failed to publish message')


@plugin.command('mesh_stats')
@plugin.example('`mesh_stats')
def mesh_stats(bot, trigger):
    """Show statistics about discovered nodes and messages."""
    with cache_lock:
        total_nodes = len(node_cache)
        by_region = defaultdict(int)
        for node in node_cache.values():
            region = node.get('region', 'Unknown')
            by_region[region] += 1

    with message_cache_lock:
        total_messages = len(message_cache)
        by_type = defaultdict(int)
        for msg in message_cache:
            msg_type = msg.get('type', 'unknown')
            by_type[msg_type] += 1

    bot.say(f"{formatter.bold('Meshtastic MQTT Statistics')}:")
    bot.say(f"Total Nodes: {total_nodes}")
    bot.say(f"Total Messages: {total_messages}")

    if by_region:
        bot.say(f"{formatter.bold('Nodes by Region')}:")
        for region in sorted(by_region.keys()):
            count = by_region[region]
            bot.say(f"  {region}: {count}")

    if by_type:
        bot.say(f"{formatter.bold('Messages by Type')}:")
        for msg_type in sorted(by_type.keys()):
            count = by_type[msg_type]
            bot.say(f"  {msg_type}: {count}")

    bot.say(f"Active Subscriptions: {len(active_subscriptions)}")
