"""
Sopel module for Currency Exchange APIs.
Supports 7 public APIs with no authentication required.
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
        'name': 'Bank of Russia',
        'description': 'Exchange rates and currency conversion',
        'link': 'https://www.cbr.ru/development/SXML/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Currency-api',
        'description': 'Free Currency Exchange Rates API with 150+ Currencies & No Rate Limits',
        'link': 'https://github.com/fawazahmed0/currency-api#readme',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Czech National Bank',
        'description': 'A collection of exchange rates',
        'link': 'https://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.xml',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Economia.Awesome',
        'description': 'Portuguese free currency prices and conversion with no rate limits',
        'link': 'https://docs.awesomeapi.com.br/api-de-moedas',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Frankfurter',
        'description': 'Exchange rates, currency conversion and time series',
        'link': 'https://www.frankfurter.app/docs',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'National Bank of Poland',
        'description': 'A collection of currency exchange rates (data in XML and JSON)',
        'link': 'http://api.nbp.pl/en.html',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'VATComply.com',
        'description': 'Exchange rates, geolocation and VAT number validation',
        'link': 'https://www.vatcomply.com/documentation',
        'https': True,
        'cors': 'yes',
    },
]

@plugin.command('currency_frankfurter')
@plugin.example('`currency_frankfurter USD EUR')
@plugin.example('`currency_frankfurter 100 USD EUR')
def currency_frankfurter(bot, trigger):
    """Convert currency using Frankfurter API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `currency_frankfurter [amount] <from> <to>')
        bot.notice(trigger.nick, 'Example: `currency_frankfurter USD EUR')
        bot.notice(trigger.nick, 'Example: `currency_frankfurter 100 USD EUR')
        return

    parts = trigger.group(2).strip().upper().split()

    if len(parts) == 2:
        # Just currencies: USD EUR
        amount = 1.0
        from_curr = parts[0]
        to_curr = parts[1]
    elif len(parts) == 3:
        # Amount and currencies: 100 USD EUR
        try:
            amount = float(parts[0])
            from_curr = parts[1]
            to_curr = parts[2]
        except ValueError:
            bot.notice(trigger.nick, 'Invalid format. Use: [amount] <from> <to>')
            return
    else:
        bot.notice(trigger.nick, 'Invalid format. Use: [amount] <from> <to>')
        return

    logger.info(f'Currency conversion: {amount} {from_curr} to {to_curr}')

    url = f'https://api.frankfurter.app/latest?from={http.quote(from_curr)}&to={http.quote(to_curr)}'

    logger.debug(f'Fetching exchange rate: {url}')
    data = http.get(url)

    if not data or 'rates' not in data:
        bot.notice(trigger.nick, 'Failed to fetch exchange rate. Please try again.')
        return

    rate = data.get('rates', {}).get(to_curr)
    if not rate:
        bot.notice(trigger.nick, f'Currency {to_curr} not found in response.')
        return

    converted = amount * rate
    date = data.get('date', 'Unknown')

    response = f"{formatter.bold(f'{amount:,.2f}')} {formatter.monospace(from_curr)} = {formatter.bold(f'{converted:,.2f}')} {formatter.monospace(to_curr)}"
    response += f" | Rate: {formatter.monospace(f'{rate:.4f}')} | Date: {date}"
    bot.say(formatter.truncate(response, max_len=400))

def setup(bot):
    """Module setup - Currency Exchange APIs loaded."""
    register_apis('currency_exchange', APIS)
    bot.memory['currency_exchange_loaded'] = True
    bot.memory['currency_exchange_count'] = 7
    logger.info('Currency Exchange module loaded')

def shutdown(bot):
    """Module shutdown."""
    bot.memory['currency_exchange_loaded'] = False
    logger.info('Currency Exchange module unloaded')
