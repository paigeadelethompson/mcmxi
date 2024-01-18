# -*- coding: utf8 -*-
"""
stocks.py - Willie stocks/yahoo finanace Module
"""

from sopel.module import commands, example
import requests
import yfinance as yf

@commands('stock', 'stocks', 'ticker')
@example('.stocks msft')
def stocks(bot, trigger):
    """.stocks msft"""
    user_input = trigger.group(2)
    stock = yf.Ticker(user_input)
    try:
        info = stock.info
        resp = "{}/{} - Current: {} {} Open: {} Close: {}".format(info['symbol'], info['shortName'], info['bid'], info['currency'], info['open'], info['previousClose'])
        bot.say(resp)
    except:
        bot.say('invalid input?')

