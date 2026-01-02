"""
Sopel module for Cryptocurrency APIs.
Supports 15 public APIs with no authentication required.
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
        'name': '1inch',
        'description': 'API for querying decentralize exchange',
        'link': 'https://1inch.io/page-api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'CoinCap',
        'description': 'Real time Cryptocurrency prices through a RESTful API',
        'link': 'https://docs.coincap.io/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'CoinGecko',
        'description': 'Cryptocurrency Price, Market, and Developer/Social Data',
        'link': 'http://www.coingecko.com/api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Coinlore',
        'description': 'Cryptocurrencies prices, volume and more',
        'link': 'https://www.coinlore.com/cryptocurrency-data-api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Coinpaprika',
        'description': 'Cryptocurrencies prices, volume and more',
        'link': 'https://api.coinpaprika.com',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'CryptAPI',
        'description': 'Cryptocurrency Payment Processor',
        'link': 'https://docs.cryptapi.io/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'CryptoCompare',
        'description': 'Cryptocurrencies Comparison',
        'link': 'https://www.cryptocompare.com/api#',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Gemini',
        'description': 'Cryptocurrencies Exchange',
        'link': 'https://docs.gemini.com/rest-api/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Mempool',
        'description': 'Bitcoin API Service focusing on the transaction fee',
        'link': 'https://mempool.space/api',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'MercadoBitcoin',
        'description': 'Brazilian Cryptocurrency Information',
        'link': 'https://api.mercadobitcoin.net/api/v4/docs',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Messari',
        'description': 'Provides API endpoints for thousands of crypto assets',
        'link': 'https://messari.io/api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Nexchange',
        'description': 'Automated cryptocurrency exchange service',
        'link': 'https://nexchange2.docs.apiary.io/',
        'https': False,
        'cors': 'yes',
    },
    {
        'name': 'Solana JSON RPC',
        'description': 'Provides various endpoints to interact with the Solana Blockchain',
        'link': 'https://docs.solana.com/developing/clients/jsonrpc-api',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Tron Network',
        'description': 'Provides various endpoints to interact with the Tron Blockchain',
        'link': 'https://developers.tron.network/reference/api-key',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'ZMOK',
        'description': 'Ethereum JSON RPC API and Web3 provider',
        'link': 'https://docs.zmok.io',
        'https': True,
        'cors': 'unknown',
    },
]




@plugin.command('crypto_coingecko')
@plugin.example('`crypto_coingecko bitcoin')
@plugin.example('`crypto_coingecko ethereum')
def crypto_coingecko(bot, trigger):
    """Get cryptocurrency price using CoinGecko API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `crypto_coingecko <coin_name>')
        bot.notice(trigger.nick, 'Example: `crypto_coingecko bitcoin')
        return

    coin = trigger.group(2).strip().lower()
    logger.info(f'Crypto price lookup: {coin}')

    # First, search for the coin
    encoded_coin = http.quote(coin)
    search_url = f'https://api.coingecko.com/api/v3/search?query={encoded_coin}'
    search_data = http.get(search_url)

    if not search_data or 'coins' not in search_data or not search_data['coins']:
        bot.notice(trigger.nick, f'Cryptocurrency "{coin}" not found.')
        return

    # Get the first result
    coin_id = search_data['coins'][0]['id']
    coin_name = search_data['coins'][0]['name']

    # Get price data
    price_url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true'
    price_data = http.get(price_url)

    if not price_data or coin_id not in price_data:
        bot.notice(trigger.nick, 'Failed to fetch price data. Please try again.')
        return

    coin_data = price_data[coin_id]
    price = coin_data.get('usd', 'N/A')
    change_24h = coin_data.get('usd_24h_change', 'N/A')

    if price != 'N/A':
        price_str = f"${price:,.2f}" if isinstance(price, (int, float)) else str(price)
        change_str = f"{change_24h:+.2f}%" if isinstance(change_24h, (int, float)) else str(change_24h)
        # Use bold for positive changes, normal for negative
        if isinstance(change_24h, (int, float)):
            change_formatted = formatter.bold(change_str) if change_24h >= 0 else change_str
        else:
            change_formatted = change_str

        response = f"{formatter.bold(coin_name)} {formatter.monospace(f'({coin_id})')}: {formatter.bold(price_str)}"
        response += f" | 24h: {change_formatted}"
        bot.say(formatter.truncate(response, max_len=400))
    else:
        bot.notice(trigger.nick, f'Price data not available for {coin_name}')


@plugin.command('crypto_coincap')
@plugin.example('`crypto_coincap bitcoin')
@plugin.example('`crypto_coincap ethereum')
def crypto_coincap(bot, trigger):
    """Get cryptocurrency price using CoinCap API."""
    # CoinCap: https://docs.coincap.io/
    # Endpoint: GET https://api.coincap.io/v2/assets?search={query}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `crypto_coincap <coin_name>')
        bot.notice(trigger.nick, 'Example: `crypto_coincap bitcoin')
        return

    coin = trigger.group(2).strip().lower()
    logger.info(f'CoinCap lookup: {coin}')

    encoded_coin = http.quote(coin)
    url = f'https://api.coincap.io/v2/assets?search={encoded_coin}'

    logger.debug(f'Searching CoinCap: {url}')
    data = http.get(url)

    if not data or 'data' not in data or not data['data']:
        bot.notice(trigger.nick, f'Cryptocurrency "{coin}" not found.')
        return

    # Get the first result
    asset = data['data'][0]
    name = asset.get('name', 'Unknown')
    symbol = asset.get('symbol', '').upper()
    price = asset.get('priceUsd', '0')
    change_24h = asset.get('changePercent24Hr', '0')
    market_cap = asset.get('marketCapUsd', '0')

    try:
        price_float = float(price)
        change_float = float(change_24h)
        market_cap_float = float(market_cap)

        price_str = f"${price_float:,.2f}"
        change_str = f"{change_float:+.2f}%"
        change_formatted = formatter.bold(change_str) if change_float >= 0 else change_str

        response = f"{formatter.bold(name)} {formatter.monospace(f'({symbol})')}: {formatter.bold(price_str)}"
        response += f" | 24h: {change_formatted}"
        if market_cap_float > 0:
            market_cap_str = f"${market_cap_float/1e9:.2f}B" if market_cap_float >= 1e9 else f"${market_cap_float/1e6:.2f}M"
            response += f" | Market Cap: {formatter.monospace(market_cap_str)}"
        bot.say(formatter.truncate(response, max_len=400))
    except (ValueError, TypeError):
        bot.notice(trigger.nick, 'Failed to parse price data.')


@plugin.command('crypto_coinpaprika')
@plugin.example('`crypto_coinpaprika bitcoin')
@plugin.example('`crypto_coinpaprika ethereum')
def crypto_coinpaprika(bot, trigger):
    """Get cryptocurrency price using Coinpaprika API."""
    # Coinpaprika: https://api.coinpaprika.com
    # Endpoint: GET https://api.coinpaprika.com/v1/search?q={query}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `crypto_coinpaprika <coin_name>')
        bot.notice(trigger.nick, 'Example: `crypto_coinpaprika bitcoin')
        return

    coin = trigger.group(2).strip().lower()
    logger.info(f'Coinpaprika lookup: {coin}')

    encoded_coin = http.quote(coin)
    search_url = f'https://api.coinpaprika.com/v1/search?q={encoded_coin}'

    logger.debug(f'Searching Coinpaprika: {search_url}')
    search_data = http.get(search_url)

    if not search_data or 'currencies' not in search_data or not search_data['currencies']:
        bot.notice(trigger.nick, f'Cryptocurrency "{coin}" not found.')
        return

    # Get the first currency result
    currency = search_data['currencies'][0]
    coin_id = currency.get('id', '')

    # Get ticker data
    ticker_url = f'https://api.coinpaprika.com/v1/tickers/{coin_id}'
    logger.debug(f'Fetching ticker: {ticker_url}')
    ticker_data = http.get(ticker_url)

    if not ticker_data:
        bot.notice(trigger.nick, 'Failed to fetch price data.')
        return

    name = ticker_data.get('name', 'Unknown')
    symbol = ticker_data.get('symbol', '').upper()
    quotes = ticker_data.get('quotes', {})
    usd_quote = quotes.get('USD', {})

    price = usd_quote.get('price', 0)
    change_24h = usd_quote.get('percent_change_24h', 0)
    market_cap = usd_quote.get('market_cap', 0)

    try:
        price_float = float(price)
        change_float = float(change_24h)
        market_cap_float = float(market_cap)

        price_str = f"${price_float:,.2f}"
        change_str = f"{change_float:+.2f}%"
        change_formatted = formatter.bold(change_str) if change_float >= 0 else change_str

        response = f"{formatter.bold(name)} {formatter.monospace(f'({symbol})')}: {formatter.bold(price_str)}"
        response += f" | 24h: {change_formatted}"
        if market_cap_float > 0:
            market_cap_str = f"${market_cap_float/1e9:.2f}B" if market_cap_float >= 1e9 else f"${market_cap_float/1e6:.2f}M"
            response += f" | Market Cap: {formatter.monospace(market_cap_str)}"
        bot.say(formatter.truncate(response, max_len=400))
    except (ValueError, TypeError):
        bot.notice(trigger.nick, 'Failed to parse price data.')


@plugin.command('crypto_coinlore')
@plugin.example('`crypto_coinlore bitcoin')
@plugin.example('`crypto_coinlore ethereum')
def crypto_coinlore(bot, trigger):
    """Get cryptocurrency price using Coinlore API."""
    # Coinlore: https://www.coinlore.com/cryptocurrency-data-api
    # Endpoint: GET https://api.coinlore.com/api/coin/search/?q={query}

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `crypto_coinlore <coin_name>')
        bot.notice(trigger.nick, 'Example: `crypto_coinlore bitcoin')
        return

    coin = trigger.group(2).strip().lower()
    logger.info(f'Coinlore lookup: {coin}')

    encoded_coin = http.quote(coin)
    search_url = f'https://api.coinlore.com/api/coin/search/?q={encoded_coin}'

    logger.debug(f'Searching Coinlore: {search_url}')
    search_data = http.get(search_url)

    if not search_data or not isinstance(search_data, list) or not search_data:
        bot.notice(trigger.nick, f'Cryptocurrency "{coin}" not found.')
        return

    # Get the first result
    coin_data = search_data[0]
    coin_id = coin_data.get('id', '')

    # Get ticker data using the coin ID
    ticker_url = f'https://api.coinlore.com/api/ticker/?id={coin_id}'
    logger.debug(f'Fetching ticker: {ticker_url}')
    ticker_data = http.get(ticker_url)

    if not ticker_data or not isinstance(ticker_data, list) or not ticker_data:
        bot.notice(trigger.nick, 'Failed to fetch price data.')
        return

    coin_info = ticker_data[0]
    name = coin_info.get('name', 'Unknown')
    symbol = coin_info.get('symbol', '').upper()
    price = coin_info.get('price_usd', '0')
    change_24h = coin_info.get('percent_change_24h', '0')
    market_cap = coin_info.get('market_cap_usd', '0')

    try:
        price_float = float(price)
        change_float = float(change_24h)
        market_cap_float = float(market_cap)

        price_str = f"${price_float:,.2f}"
        change_str = f"{change_float:+.2f}%"
        change_formatted = formatter.bold(change_str) if change_float >= 0 else change_str

        response = f"{formatter.bold(name)} {formatter.monospace(f'({symbol})')}: {formatter.bold(price_str)}"
        response += f" | 24h: {change_formatted}"
        if market_cap_float > 0:
            market_cap_str = f"${market_cap_float/1e9:.2f}B" if market_cap_float >= 1e9 else f"${market_cap_float/1e6:.2f}M"
            response += f" | Market Cap: {formatter.monospace(market_cap_str)}"
        bot.say(formatter.truncate(response, max_len=400))
    except (ValueError, TypeError):
        bot.notice(trigger.nick, 'Failed to parse price data.')


@plugin.command('crypto_cryptocompare')
@plugin.example('`crypto_cryptocompare BTC')
@plugin.example('`crypto_cryptocompare ETH')
def crypto_cryptocompare(bot, trigger):
    """Get cryptocurrency price using CryptoCompare API."""
    # CryptoCompare: https://www.cryptocompare.com/api#
    # Endpoint: GET https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `crypto_cryptocompare <coin_symbol>')
        bot.notice(trigger.nick, 'Example: `crypto_cryptocompare BTC')
        return

    symbol = trigger.group(2).strip().upper()
    logger.info(f'CryptoCompare lookup: {symbol}')

    url = f'https://min-api.cryptocompare.com/data/price?fsym={http.quote(symbol)}&tsyms=USD'

    logger.debug(f'Fetching price: {url}')
    data = http.get(url)

    if not data or 'USD' not in data:
        if 'Response' in data and data['Response'] == 'Error':
            error_msg = data.get('Message', 'Unknown error')
            bot.notice(trigger.nick, f'Error: {error_msg}')
        else:
            bot.notice(trigger.nick, f'Failed to fetch price for {symbol}.')
        return

    price = data.get('USD', 0)

    try:
        price_float = float(price)
        price_str = f"${price_float:,.2f}"
        response = f"{formatter.bold(symbol)}: {formatter.bold(price_str)}"
        bot.say(formatter.truncate(response, max_len=400))
    except (ValueError, TypeError):
        bot.notice(trigger.nick, 'Failed to parse price data.')


@plugin.command('crypto_mempool')
@plugin.example('`crypto_mempool')
def crypto_mempool(bot, trigger):
    """Get Bitcoin transaction fees using Mempool API."""
    logger.info('Mempool Bitcoin fees lookup')

    url = 'https://mempool.space/api/v1/fees/recommended'
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to fetch Bitcoin fees.')
        return

    fastest_fee = data.get('fastestFee', 0)
    half_hour_fee = data.get('halfHourFee', 0)
    hour_fee = data.get('hourFee', 0)
    economy_fee = data.get('economyFee', 0)
    minimum_fee = data.get('minimumFee', 0)

    fee_data = {
        'Fastest': fastest_fee,
        '30min': half_hour_fee,
        '1hr': hour_fee,
        'Economy': economy_fee,
        'Min': minimum_fee,
    }

    bot.say(f"{formatter.bold('Bitcoin Fees')} (sat/vB):")
    chart = formatter.horizontal_bar(
        list(fee_data.values()),
        labels=list(fee_data.keys()),
        width=30,
        show_values=True
    )
    for line in chart.split('\n'):
        bot.say(line)


def setup(bot):
    """Module setup - Cryptocurrency APIs loaded."""
    register_apis('cryptocurrency', APIS)
    bot.memory['cryptocurrency_loaded'] = True
    bot.memory['cryptocurrency_count'] = 15
    logger.info('Cryptocurrency module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['cryptocurrency_loaded'] = False
    logger.info('Cryptocurrency module unloaded')
