"""
Sopel module for Text Analysis APIs.
Supports 2 public APIs with no authentication required.
"""

from sopel import plugin
import json
import sys
import os
# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get_module_logger, HTTPClient, IRCFormatter

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


@plugin.command('text_analysis')
@plugin.command('textanalysis')
@plugin.example(f'.text_analysis')
def text_analysis_list(bot, trigger):
    """List all available Text Analysis APIs."""
    bot.say(f'Available Text Analysis APIs (2):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .text_analysis_info <name> for details')


@plugin.command('text_analysis_info')
@plugin.example(f'.text_analysis_info <name>')
def text_analysis_info(bot, trigger):
    """Get information about a specific Text Analysis API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .text_analysis_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('text_analysis_search')
@plugin.example(f'.text_analysis_search <query>')
def text_analysis_search(bot, trigger):
    """Search Text Analysis APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .text_analysis_search <query>')
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


@plugin.command('translate_libretranslate')
@plugin.example('.translate_libretranslate Hello es')
@plugin.example('.translate_libretranslate Bonjour en')
def translate_libretranslate(bot, trigger):
    """Translate text using LibreTranslate API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .translate_libretranslate <text> <target_lang>')
        bot.notice(trigger.nick, 'Example: .translate_libretranslate Hello es')
        return
    
    parts = trigger.group(2).strip().split(None, 1)
    if len(parts) < 2:
        bot.notice(trigger.nick, 'Usage: .translate_libretranslate <text> <target_lang>')
        bot.notice(trigger.nick, 'Supported languages: en, es, fr, de, it, pt, ru, ja, zh, etc.')
        return
    
    target_lang = parts[0].lower()
    text = parts[1]
    
    logger.info(f'Translation: {text[:50]}... to {target_lang}')
    
    # LibreTranslate public API endpoint
    url = 'https://libretranslate.com/translate'
    
    payload = {
        'q': text,
        'source': 'auto',  # Auto-detect source language
        'target': target_lang,
        'format': 'text'
    }
    
    import json as json_module
    
    data = json_module.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    
    logger.debug(f'Translating text: {url}')
    response_data = http.post(url, data=data, headers=headers)
    
    if not response_data:
        bot.notice(trigger.nick, 'Translation service error. Please try again.')
        return
    
    if 'translatedText' in response_data:
        translated = response_data['translatedText']
        detected_lang = response_data.get('detectedLanguage', {}).get('language', 'auto')
        
        response_text = f"{formatter.bold(text)} {formatter.monospace(f'({detected_lang})')} → {formatter.bold(translated)} {formatter.monospace(f'({target_lang})')}"
        bot.say(formatter.truncate(response_text, max_len=400))
    else:
        bot.notice(trigger.nick, 'Translation failed. Please try again.')


def setup(bot):
    """Module setup - Text Analysis APIs loaded."""
    bot.memory['text_analysis_loaded'] = True
    bot.memory['text_analysis_count'] = 2
    logger.info('Text Analysis module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['text_analysis_loaded'] = False
    logger.info('Text Analysis module unloaded')
