
# -*- coding: utf8 -*-
"""
voide_join.py - Willie giphy Module
"""

from sopel.module import commands, rule, event
import threading

def give_voice(bot, trigger, username):
    channel = trigger.sender
    return bot.write(['MODE', channel, '+v',username])

@event('JOIN')
@rule(r'.*')
def voice_join(bot, trigger):
    if  trigger.nick == bot.nick:
        return
    timer = threading.Timer(30.0, give_voice, args=[bot, trigger, trigger.nick])
    timer.start()
    
    