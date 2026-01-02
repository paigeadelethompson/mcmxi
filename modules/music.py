"""
Sopel module for Music APIs.
Supports 8 public APIs with no authentication required.
"""

import os
import sys

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, IRCFormatter, get_module_logger, register_apis

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)
formatter = IRCFormatter()


# API definitions
APIS = [
    {
        'name': 'Bandsintown',
        'description': 'Music Events',
        'link': 'https://app.swaggerhub.com/apis/Bandsintown/PublicAPI/3.0.0',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Gaana',
        'description': 'API to retrieve song information from Gaana',
        'link': 'https://github.com/cyberboysumanjay/GaanaAPI',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Genrenator',
        'description': 'Music genre generator',
        'link': 'https://binaryjazz.us/genrenator-api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'JioSaavn',
        'description': 'API to retrieve song information, album meta data and many more from JioSaavn',
        'link': 'https://github.com/cyberboysumanjay/JioSaavnAPI',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'LRCLIB',
        'description': 'Crowdsourced lyrics',
        'link': 'https://lrclib.net/docs',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'MusicBrainz',
        'description': 'Music',
        'link': 'https://musicbrainz.org/doc/Development/XML_Web_Service/Version_2',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Openwhyd',
        'description': 'Download curated playlists of streaming tracks (YouTube, SoundCloud, etc...)',
        'link': 'https://openwhyd.github.io/openwhyd/API',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Radio Browser',
        'description': 'List of internet radio stations',
        'link': 'https://api.radio-browser.info/',
        'https': True,
        'cors': 'yes',
    },
]




@plugin.command('radio_radiobrowser')
@plugin.example('`radio_radiobrowser jazz')
@plugin.example('`radio_radiobrowser country')
def radio_radiobrowser(bot, trigger):
    """Search for internet radio stations using Radio Browser API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `radio_radiobrowser <genre/name>')
        return

    query = trigger.group(2).strip()
    logger.info(f'Radio search: {query}')

    encoded_query = http.quote(query)
    url = f'https://de1.api.radio-browser.info/json/stations/search?name={encoded_query}&limit=3'

    logger.debug(f'Searching radio stations: {url}')
    data = http.get(url)

    if not data or not isinstance(data, list):
        bot.notice(trigger.nick, 'No radio stations found or API error. Please try again.')
        return

    results = data[:3]

    if not results:
        bot.notice(trigger.nick, f'No radio stations found for "{query}"')
        return

    bot.say(f'Found {len(results)} station(s) for "{query}":')
    for station in results:
        name = station.get('name', 'Unknown')
        country = station.get('country', '')
        tags = station.get('tags', '')
        station.get('url', '')

        response = f"{formatter.bold(name)}"
        if country:
            response += f" {formatter.italic(f'({country})')}"
        if tags:
            tags_list = tags.split(',')[:2]
            response += f" | Tags: {formatter.monospace(', '.join(tags_list))}"

        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('music_lrclib')
@plugin.example('`music_lrclib "The Beatles" "Hey Jude"')
def music_lrclib(bot, trigger):
    """Search for lyrics using LRCLIB API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `music_lrclib "<artist>" "<song>"')
        bot.notice(trigger.nick, 'Example: `music_lrclib "The Beatles" "Hey Jude"')
        return

    args = trigger.group(2).strip()
    # Parse artist and song (could be quoted or space-separated)
    parts = args.split('"')
    if len(parts) >= 3:
        artist = parts[1].strip()
        song = parts[3].strip() if len(parts) > 3 else ''
    else:
        # Try space-separated
        parts = args.split(None, 1)
        if len(parts) >= 2:
            artist = parts[0]
            song = parts[1]
        else:
            bot.notice(trigger.nick, 'Usage: `music_lrclib "<artist>" "<song>"')
            return

    if not artist or not song:
        bot.notice(trigger.nick, 'Usage: `music_lrclib "<artist>" "<song>"')
        return

    logger.info(f'LRCLIB lyrics search: {artist} - {song}')

    encoded_artist = http.quote(artist)
    encoded_song = http.quote(song)
    url = f'https://lrclib.net/api/search?artist_name={encoded_artist}&track_name={encoded_song}'

    logger.debug(f'Searching lyrics: {url}')
    data = http.get(url, timeout=10)

    if not data or not isinstance(data, list) or len(data) == 0:
        bot.notice(trigger.nick, f'No lyrics found for "{artist}" - "{song}"')
        return

    result = data[0]  # Get first result
    lyrics = result.get('syncedLyrics', '')
    plain_lyrics = result.get('plainLyrics', '')
    artist_name = result.get('artistName', artist)
    track_name = result.get('trackName', song)
    album_name = result.get('albumName', '')
    duration = result.get('duration', 0)

    bot.say(
        f"{formatter.bold(f'{artist_name} - {track_name}')}"
        f"{f' ({album_name})' if album_name else ''}"
    )

    if duration:
        bot.say(f"Duration: {formatter.monospace(f'{duration}s')}")

    # Show lyrics preview (first 200 chars)
    lyrics_text = plain_lyrics if plain_lyrics else lyrics
    if lyrics_text:
        preview = lyrics_text[:200].replace('\n', ' ')
        bot.say(formatter.truncate(f"Lyrics: {preview}...", max_len=400))
    else:
        bot.notice(trigger.nick, 'No lyrics text available')


@plugin.command('music_genrenator')
@plugin.example('`music_genrenator')
def music_genrenator(bot, trigger):
    """Generate a random music genre using Genrenator API."""
    logger.info('Generating random music genre')

    url = 'https://binaryjazz.us/wp-json/genrenator/v1/genre/'

    logger.debug(f'Getting genre: {url}')
    data = http.get(url, timeout=10)

    if not data:
        bot.notice(trigger.nick, 'Failed to generate genre.')
        return

    # Genrenator returns a simple string
    genre = data if isinstance(data, str) else data.get('genre', 'Unknown')

    bot.say(f"Random genre: {formatter.bold(genre)}")


@plugin.command('music_musicbrainz')
@plugin.example('`music_musicbrainz artist "The Beatles"')
@plugin.example('`music_musicbrainz release "Abbey Road"')
def music_musicbrainz(bot, trigger):
    """Search MusicBrainz database for artists, releases, or recordings."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `music_musicbrainz <type> <query>')
        bot.notice(trigger.nick, 'Types: artist, release, recording')
        bot.notice(trigger.nick, 'Example: `music_musicbrainz artist "The Beatles"')
        return

    args = trigger.group(2).strip().split(None, 1)
    if len(args) < 2:
        bot.notice(trigger.nick, 'Usage: `music_musicbrainz <type> <query>')
        return

    search_type = args[0].lower()
    query = args[1].strip().strip('"')

    if search_type not in ['artist', 'release', 'recording']:
        bot.notice(trigger.nick, 'Type must be: artist, release, or recording')
        return

    logger.info(f'MusicBrainz search: {search_type} - {query}')

    encoded_query = http.quote(query)
    url = f'https://musicbrainz.org/ws/2/{search_type}/?query={encoded_query}&fmt=json&limit=3'

    logger.debug(f'Searching MusicBrainz: {url}')
    data = http.get(url, timeout=10)

    if not data or search_type not in data or not data[search_type + 's']:
        bot.notice(trigger.nick, f'No {search_type}s found for "{query}"')
        return

    results = data[search_type + 's'][:3]

    bot.say(
        f"{formatter.bold(f'MusicBrainz {search_type.title()}s')} "
        f"for {formatter.monospace(query)}:"
    )

    for i, item in enumerate(results, 1):
        name = item.get('name', 'Unknown')
        mbid = item.get('id', '')
        disambiguation = item.get('disambiguation', '')

        response_parts = [f"{i}. {formatter.bold(name)}"]

        if disambiguation:
            response_parts.append(f"({disambiguation})")

        if search_type == 'release':
            date = item.get('date', '')
            if date:
                response_parts.append(f"Released: {formatter.monospace(date)}")

        bot.say(' | '.join(response_parts))

        if mbid:
            bot.say(f"  MBID: {formatter.monospace(mbid)}")


def setup(bot):
    """Module setup - Music APIs loaded."""
    register_apis('music', APIS)
    bot.memory['music_loaded'] = True
    bot.memory['music_count'] = 8
    logger.info('Music module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['music_loaded'] = False
    logger.info('Music module unloaded')
