
# -*- coding: utf8 -*-
"""
jisho.py - Willie giphy Module
"""

from sopel.module import commands, example
import requests
from alpha_vantage.timeseries import TimeSeries
from collections import OrderedDict

@commands('stock', 'stocks', 'ticker')
@example('.stock MSFT')
def stocks(bot, trigger):
    """.stock MSFT"""
    user_input = trigger.group(2)
    ts = TimeSeries(key=bot.config.apikeys.alphavantage_api_key)
    try:
        data, meta_data = ts.get_daily(user_input)
    except:
        bot.say("invalid ticker/input. Blame bob.")
        return 
    ordered = OrderedDict(sorted(data.items(), key=lambda t: t[0], reverse=True))
    ordered_list = list(ordered.items())
    today = ordered_list[0][1]["4. close"]
    prev = ordered_list[20][1]["4. close"]
    diff = today - prev
    signal = "\u2213"
    if diff > 0:
        signal = "\u2191"
    else:
        signal = "\u2193"
    percent = "{} {}%".format(signal, round(diff/prev))
    response_string = "{} - Most Recent: {} 30 Day Change: {}".format(user_input, today, percent)
    bot.say(response_string)