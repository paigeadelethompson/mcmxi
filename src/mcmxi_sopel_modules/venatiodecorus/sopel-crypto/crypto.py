import sopel.module
from requests import get
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

# Init
coin_list = cg.get_coins_list()

# Lookup coin name from abbreviation
def find_coin_name(s):
    s = s.lower()
    for coin in coin_list:
        if coin['id'].lower() == s or coin['symbol'].lower() == s:
            return coin

# Commands
@sopel.module.commands('crypto')
@sopel.module.example('.crypto [bitcoin(,ethereum,...)]')
def crypto(bot, trigger):
    # No argument, display default list
    if trigger.group(2) == None:
        defaults = ['bitcoin','ethereum','polkadot','cardano']
        res = cg.get_price(ids=defaults, vs_currencies='usd')
        output = ""
        for coin in res:
            output += ("{}: {} ").format(coin, res[coin]['usd'])
        bot.say(output)
        return

    coins = trigger.group(2).strip().lower().split(',')
    find_coins = []
    for coin in coins:
        print('finding coin: ' + coin)
        find_coins.append(find_coin_name(coin)['id'])

    res = cg.get_price(ids=find_coins, vs_currencies='usd')
    output = ""
    for coin in res:
        output += ("{}: {} ").format(coin, res[coin]['usd'])

    bot.say(output)