"""
Sopel module for Dictionaries APIs.
Supports 4 public APIs with no authentication required.
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
        'name': 'Chinese Character Web',
        'description': 'Chinese character definitions and pronunciations',
        'link': 'http://ccdb.hemiola.com/',
        'https': False,
        'cors': 'no',
    },
    {
        'name': 'Chinese Text Project',
        'description': 'Online open-access digital library for pre-modern Chinese texts',
        'link': 'https://ctext.org/tools/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Free Dictionary',
        'description': 'Definitions, phonetics, pronounciations, parts of speech, examples, synonyms',
        'link': 'https://dictionaryapi.dev/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Wiktionary',
        'description': 'Collaborative dictionary data',
        'link': 'https://en.wiktionary.org/w/api.php',
        'https': True,
        'cors': 'yes',
    },
]







@plugin.command('dict_freedictionary')
@plugin.example('`dict_freedictionary hello')
@plugin.example('`dict_freedictionary computer')
def dict_freedictionary(bot, trigger):
    """Look up word definition using Free Dictionary API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `dict_freedictionary <word>')
        return

    word = trigger.group(2).strip()
    logger.info(f'Dictionary lookup: {word}')

    encoded_word = http.quote(word)
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{encoded_word}'

    logger.debug(f'Fetching definition: {url}')
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, f'Word "{word}" not found.')
        return

    # API returns array of entries
    if not isinstance(data, list) or not data:
        bot.notice(trigger.nick, f'Word "{word}" not found.')
        return

    entry = data[0]  # Get first entry
    word_text = entry.get('word', word)
    meanings = entry.get('meanings', [])

    if not meanings:
        bot.notice(trigger.nick, f'No definitions found for "{word}"')
        return

    # Get first meaning with first definition
    first_meaning = meanings[0]
    part_of_speech = first_meaning.get('partOfSpeech', '')
    definitions = first_meaning.get('definitions', [])

    if not definitions:
        bot.notice(trigger.nick, f'No definitions found for "{word}"')
        return

    definition = definitions[0].get('definition', 'No definition available')
    example = definitions[0].get('example', '')

    response = f"{formatter.bold(word_text)}"
    if part_of_speech:
        response += f" {formatter.monospace(f'({part_of_speech})')}"
    response += f": {definition}"

    bot.say(formatter.truncate(response, max_len=400))

    if example:
        bot.say(f"{formatter.italic('Example:')} {formatter.italic(example)}")


def setup(bot):
    """Module setup - Dictionaries APIs loaded."""
    register_apis('dictionaries', APIS)
    bot.memory['dictionaries_loaded'] = True
    bot.memory['dictionaries_count'] = 4
    logger.info('Dictionaries module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['dictionaries_loaded'] = False
    logger.info('Dictionaries module unloaded')
