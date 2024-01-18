
# -*- coding: utf8 -*-
"""
crypto.py - Willie crypto Module
"""

from sopel.module import commands, example
import requests
import re
from collections import OrderedDict

single = "^([a-zA-Z]+)\s([a-zA-Z]+)$"
single_to = "^([a-zA-Z]+)\sto\s([a-zA-Z]+)$"
digit = "^(\d+)\s([a-zA-Z]+)\sto\s([a-zA-Z]+)$"
digit_to = "^(\d+)\s([a-zA-Z]+)\s([a-zA-Z]+)$"

@commands('crypto', 'coin')
@example('.crypto btc usd')
def crypto(bot, trigger):
    """.crypto btc usd"""
    user_input = trigger.group(2).strip()
    single_m = re.findall(single, user_input, re.I) or re.findall(single_to, user_input, re.I)
    digit_m = re.findall(digit, user_input, re.I) or re.findall(digit_to, user_input, re.I)    
    start = "btc"
    end = "usd"
    num = 1
    if single_m:
      start = single_m[0][0]
      end = single_m[0][1]
    if double_m:
      num = double_m[0][1]
      start = double_m[0][1]
      end = double_m[0][2]
    if len(user_input.split()) == 1:
      start = user_input
      
    url = "https://rest.coinapi.io/v1/exchangerate/{}/{}".format(start.upper(), end.upper())
    headers = {'X-CoinAPI-Key' : bot.config.apikeys.coinapi_api_key}
    response = requests.get(url, headers=headers).json()
    if response['error']:
      bot.say("something went wrong")
      return
    response_string = "{} {} = {} {}".format(num, response["asset_id_base"], round(num * response["rate"], 2), response["asset_id_quote"])
    bot.say(response_string)
