# -*- coding: utf8 -*-
"""
urbandictionary.py - bot Urban Dictionary Module
Copyright 2013, Jin Park - jinpark.net
Licensed under the Eiffel Forum License 2.

http://inamidst.com/bot/
"""

from sopel import module
import requests
import urllib.request, urllib.parse, urllib.error
import string
import re

@module.commands('ud')
@module.example('.ud cat --def 1')
def ud(bot, trigger):
    """Urban Dictionary Definition"""
    full_input = trigger.group(2)
    page_num = 0
    htmlinput = full_input
    if re.search("--def", full_input):
        split_input = re.split("--def", full_input)
        page_num = int(split_input[-1]) - 1
        htmlinput = split_input[0]

    htmlinput = urllib.parse.quote(htmlinput.encode("utf-8"))
    url = 'http://api.urbandictionary.com/v0/define?term=' + htmlinput
    try:
        json_response = requests.get(url).json()
        num_def = len(json_response['list'])
        defin = "({}/{}) ({}\u2191/{}\u2193) {}: {}".format(page_num + 1, num_def, json_response['list'][page_num]['thumbs_up'], json_response['list'][page_num]['thumbs_down'], json_response['list'][page_num]['word'], json_response['list'][page_num]['definition'])
        permalink = json_response['list'][page_num]['permalink']
    except:
        defin = 'Bob broke something.'
    defin = defin.replace('\r\n', ' ').replace('[word]', ' ').replace('[/word]', ' ')
    if len(defin) > 420:
        defin_1 = defin[:420]
        defin_2 = defin[420:840]
    else:
        defin_1 = ''
        defin_2 = ''

    if defin_1:
        bot.say(defin_1)
        if defin_2:
            bot.say(defin_2)
    else:
        bot.say(defin)

@module.commands('ude')
@module.example('.ude cat --def 1')
def ude(bot, trigger):
    """Urban Dictionary Example"""
    full_input = trigger.group(2)
    page_num = 0
    htmlinput = full_input
    if re.search("--def", full_input):
        split_input = re.split("--def", full_input)
        page_num = int(split_input[-1]) - 1
        htmlinput = split_input[0]

    htmlinput = urllib.parse.quote(htmlinput.encode("utf-8"))
    url = 'http://api.urbandictionary.com/v0/define?term=' + htmlinput
    try:
        json_response = requests.get(url).json()
        num_def = len(json_response['list'])
        defin = "({}/{}) {}: {}".format(page_num + 1, num_def, json_response['list'][page_num]['word'], json_response['list'][page_num]['example'])
        defin = defin.replace('\r\n', ' ')
    except:
        defin = 'No urban dictionary example found.'
    bot.say(defin)

