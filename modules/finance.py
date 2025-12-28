"""
Sopel module for Finance APIs.
Supports 11 public APIs with no authentication required.
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
        'name': 'ArgentoFX',
        'description': 'Real-time foreign exchange rates for Argentina',
        'link': 'https://fastapiproject-1-eziw.onrender.com/docs',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Binlist',
        'description': 'Public access to a database of IIN/BIN information',
        'link': 'https://binlist.net/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Bullbear Advisors',
        'description': "See strong buy and sell signals the day they occur. Get today\'s stocks that closed with a strong Bullish or Bearish candlestick.",
        'link': 'https://rapidapi.com/otha1920/api/bullbear-advisor',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'DolarAPI',
        'description': 'Real-time exchange rates for Latin American currencies',
        'link': 'https://dolarapi.com/docs/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Econdb',
        'description': 'Global macroeconomic data',
        'link': 'https://www.econdb.com/api/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Fed Treasury',
        'description': 'U.S. Department of the Treasury Data',
        'link': 'https://fiscaldata.treasury.gov/api-documentation/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Indian Mutual Fund',
        'description': 'Get complete history of India Mutual Funds Data',
        'link': 'https://www.mfapi.in/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Portfolio Optimizer',
        'description': 'Portfolio analysis and optimization',
        'link': 'https://portfoliooptimizer.io/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Razorpay IFSC',
        'description': 'Indian Financial Systems Code (Bank Branch Codes)',
        'link': 'https://razorpay.com/docs/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'SEC EDGAR Data',
        'description': 'API to access annual reports of public US companies',
        'link': 'https://www.sec.gov/search-filings/edgar-application-programming-interfaces',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'WallstreetBets',
        'description': 'WallstreetBets Stock Comments Sentiment Analysis',
        'link': 'https://dashboard.nbshare.io/apps/reddit/api/',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('finance')
@plugin.command('finance')
@plugin.example(f'.finance')
def finance_list(bot, trigger):
    """List all available Finance APIs."""
    bot.say(f'Available Finance APIs (11):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .finance_info <name> for details')


@plugin.command('finance_info')
@plugin.example(f'.finance_info <name>')
def finance_info(bot, trigger):
    """Get information about a specific Finance API."""
    if not trigger.group(2):
        bot.say(f'Usage: .finance_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('finance_search')
@plugin.example(f'.finance_search <query>')
def finance_search(bot, trigger):
    """Search Finance APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .finance_search <query>')
        return

    query = trigger.group(2).strip().lower()
    results = []
    for api in APIS:
        if (query in api['name'].lower() or query in api['description'].lower()):
            results.append(api)

    if not results:
        bot.say(f'No APIs found matching: {trigger.group(2)}')
        return

    bot.say(f'Found {len(results)} API(s):')
    for api in results[:5]:  # Show first 5 results
        bot.say(f"- {api['name']}: {api['description'][:60]}")
    if len(results) > 5:
        bot.say(f'... and {len(results) - 5} more results')


def setup(bot):
    """Module setup - Finance APIs loaded."""
    bot.memory['finance_loaded'] = True
    bot.memory['finance_count'] = 11


def shutdown(bot):
    """Module shutdown."""
    bot.memory['finance_loaded'] = False


@plugin.command('currency_dolarapi')
@plugin.example('.currency_dolarapi')
def currency_dolarapi(bot, trigger):
    """Get real-time exchange rates from DolarAPI for Latin American currencies."""
    # DolarAPI: https://dolarapi.com/docs/
    # Endpoint: GET https://dolarapi.com/v1/dolares
    
    logger.info('DolarAPI currency lookup')
    
    url = 'https://dolarapi.com/v1/dolares'
    
    logger.debug(f'Fetching exchange rates: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to fetch exchange rates from DolarAPI.')
        return
    
    if not isinstance(data, list) or len(data) == 0:
        bot.notice(trigger.nick, 'No exchange rate data available.')
        return
    
    # Show first 3 exchange rates
    bot.say(f'{formatter.bold("DolarAPI Exchange Rates")} (Argentina):')
    for rate in data[:3]:
        casa = rate.get('casa', 'Unknown')
        nombre = rate.get('nombre', 'Unknown')
        compra = rate.get('compra', 0)
        venta = rate.get('venta', 0)
        fecha_actualizacion = rate.get('fechaActualizacion', 'Unknown')
        
        response = f"{formatter.bold(nombre)} ({formatter.monospace(casa)})"
        if compra:
            response += f" | Buy: {formatter.bold(str(compra))}"
        if venta:
            response += f" | Sell: {formatter.bold(str(venta))}"
        if fecha_actualizacion:
            response += f" | Updated: {formatter.monospace(fecha_actualizacion[:10])}"
        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('bin_binlist')
@plugin.example('.bin_binlist 45717360')
def bin_binlist(bot, trigger):
    """Look up IIN/BIN information for a credit/debit card number using Binlist API."""
    # Binlist: https://binlist.net/
    # Endpoint: GET https://lookup.binlist.net/{bin}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .bin_binlist <first_6_digits>')
        bot.notice(trigger.nick, 'Example: .bin_binlist 45717360')
        return
    
    bin_number = trigger.group(2).strip()
    
    # Validate it's numeric and 6-8 digits
    if not bin_number.isdigit() or len(bin_number) < 6 or len(bin_number) > 8:
        bot.notice(trigger.nick, 'BIN must be 6-8 digits.')
        return
    
    logger.info(f'Binlist lookup: {bin_number}')
    
    url = f'https://lookup.binlist.net/{bin_number}'
    
    logger.debug(f'Looking up BIN: {url}')
    data = http.get(url, headers={'Accept-Version': '3'})
    
    if not data:
        bot.notice(trigger.nick, f'BIN "{bin_number}" not found or API error.')
        return
    
    # Parse response
    scheme = data.get('scheme', 'Unknown')
    card_type = data.get('type', 'Unknown')
    brand = data.get('brand', 'Unknown')
    country_name = data.get('country', {}).get('name', 'Unknown')
    country_emoji = data.get('country', {}).get('emoji', '')
    bank_name = data.get('bank', {}).get('name', 'Unknown')
    
    response = f"{formatter.bold('BIN')} {formatter.monospace(bin_number)}"
    if brand:
        response += f" | {formatter.bold(brand)}"
    if card_type:
        response += f" {formatter.italic(card_type)}"
    if scheme:
        response += f" | Scheme: {formatter.monospace(scheme)}"
    if bank_name and bank_name != 'Unknown':
        response += f" | Bank: {formatter.italic(bank_name)}"
    if country_name and country_name != 'Unknown':
        response += f" | Country: {formatter.italic(country_name)} {country_emoji}"
    
    bot.say(formatter.truncate(response, max_len=400))
