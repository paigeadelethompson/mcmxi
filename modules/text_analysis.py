"""
Sopel module for Text Analysis APIs.
Supports 2 public APIs with no authentication required.
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
        'name': 'LanguageTool',
        'description': 'Style and Grammar Checker for 25+ Languages',
        'link': 'https://languagetool.org/http-api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'LibreTranslate',
        'description': 'Translation tool with 17 available languages',
        'link': 'https://libretranslate.com/docs',
        'https': True,
        'cors': 'unknown',
    },
]

@plugin.command('translate_libretranslate')
@plugin.example('`translate_libretranslate Hello es')
@plugin.example('`translate_libretranslate Bonjour en')
def translate_libretranslate(bot, trigger):
    """Translate text using LibreTranslate API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `translate_libretranslate <text> <target_lang>')
        bot.notice(trigger.nick, 'Example: `translate_libretranslate Hello es')
        return

    parts = trigger.group(2).strip().split(None, 1)
    if len(parts) < 2:
        bot.notice(trigger.nick, 'Usage: `translate_libretranslate <text> <target_lang>')
        bot.notice(trigger.nick, 'Supported languages: en, es, fr, de, it, pt, ru, ja, zh, etc.')
        return

    parts[0].lower()
    parts[1]

def setup(bot):
    """Module setup - Text Analysis APIs loaded."""
    register_apis('text_analysis', APIS)
    bot.memory['text_analysis_loaded'] = True
    bot.memory['text_analysis_count'] = 2
    logger.info('Text Analysis module loaded')

def shutdown(bot):
    """Module shutdown."""
    bot.memory['text_analysis_loaded'] = False
    logger.info('Text Analysis module unloaded')
