"""
Sopel module for Anime APIs.
Supports 10 public APIs with no authentication required.
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
        'name': 'AnimeNewsNetwork',
        'description': 'Anime industry news',
        'link': 'https://www.animenewsnetwork.com/encyclopedia/api.php',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Dattebayo API',
        'description': 'Dattebayo: Your Ultimate Naruto Anime API',
        'link': 'https://api-dattebayo.vercel.app/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Dragon Ball',
        'description': 'An easy to use Dragon Ball API',
        'link': 'https://web.dragonball-api.com',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Jikan',
        'description': 'Unofficial MyAnimeList API',
        'link': 'https://jikan.moe',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'NekosBest',
        'description': 'Neko Images & Anime roleplaying GIFs',
        'link': 'https://docs.nekos.best',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Nekosia API',
        'description': 'Anime API with cute random images. Dominated colors & compressed images & avoiding duplicates.',
        'link': 'https://nekosia.cat',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'PokéAPI',
        'description': 'Pokémon data, including imagery',
        'link': 'https://pokeapi.co',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Trace Moe',
        'description': 'A useful tool to get the exact scene of an anime from a screenshot',
        'link': 'https://soruly.github.io/trace.moe-api/#/',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Waifu.im',
        'description': 'Get waifu pictures from an archive of over 4000 images and multiple tags',
        'link': 'https://waifu.im/docs',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Waifu.pics',
        'description': 'Image sharing platform for anime images',
        'link': 'https://waifu.pics/docs',
        'https': True,
        'cors': 'no',
    },
]

@plugin.command('anime_jikan')
@plugin.example('`anime_jikan naruto')
@plugin.example('`anime_jikan 1')
def anime_jikan(bot, trigger):
    """Search for anime using Jikan (MyAnimeList) API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `anime_jikan <anime_name> or .anime_jikan <anime_id>')
        return

    query = trigger.group(2).strip()
    logger.info(f'Anime search: {query}')

    if query.isdigit():
        get_anime_by_id(bot, trigger.nick, int(query))
    else:
        search_anime(bot, trigger.nick, query)


def search_anime(bot, nick: str, query: str):
    """Search for anime by name."""
    encoded_query = http.quote(query)
    url = f'https://api.jikan.moe/v4/anime?q={encoded_query}&limit=3'

    logger.debug(f'Searching anime: {url}')
    data = http.get(url)

    if not data or 'data' not in data:
        bot.notice(nick, 'No anime found or API error. Please try again.')
        return

    results = data.get('data', [])[:3]

    if not results:
        bot.notice(nick, f'No anime found for "{query}"')
        return

    bot.say(f'Found {len(results)} result(s) for "{query}":')
    for anime in results:
        title = anime.get('title', 'Unknown')
        score = anime.get('score', 'N/A')
        episodes = anime.get('episodes', '?')
        status = anime.get('status', 'Unknown')
        mal_id = anime.get('mal_id', '')

        response = f"{formatter.bold(title)}"
        if score and score != 'N/A':
            response += f" | Score: {formatter.bold(f'{score}/10')}"
        response += f" | Episodes: {formatter.monospace(str(episodes))} | Status: {formatter.italic(status)}"
        if mal_id:
            response += f" | ID: {formatter.monospace(str(mal_id))}"

        bot.say(formatter.truncate(response, max_len=400))


def get_anime_by_id(bot, nick: str, anime_id: int):
    """Get anime details by MyAnimeList ID."""
    url = f'https://api.jikan.moe/v4/anime/{anime_id}/full'

    logger.debug(f'Fetching anime by ID: {url}')
    data = http.get(url)

    if not data or 'data' not in data:
        bot.notice(nick, f'Anime with ID {anime_id} not found.')
        return

    anime = data['data']
    title = anime.get('title', 'Unknown')
    title_english = anime.get('title_english', '')
    score = anime.get('score', 'N/A')
    episodes = anime.get('episodes', '?')
    status = anime.get('status', 'Unknown')
    synopsis = anime.get('synopsis', 'No synopsis available.')

    response = f"{formatter.bold(title)}"
    if title_english and title_english != title:
        response += f" {formatter.italic(f'({title_english})')}"
    if score and score != 'N/A':
        response += f" | Score: {formatter.bold(f'{score}/10')}"
    response += f" | Episodes: {formatter.monospace(str(episodes))} | Status: {formatter.italic(status)}"
    bot.say(formatter.truncate(response, max_len=400))

    if synopsis and synopsis != 'No synopsis available.':
        synopsis_short = formatter.truncate(synopsis.replace('\n', ' '), max_len=300)
        bot.say(f"{formatter.italic('Synopsis:')} {synopsis_short}")


def setup(bot):
    """Module setup - Anime APIs loaded."""
    register_apis('anime', APIS)
    bot.memory['anime_loaded'] = True
    bot.memory['anime_count'] = 10
    logger.info('Anime module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['anime_loaded'] = False
    logger.info('Anime module unloaded')
