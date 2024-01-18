"""
slap.py - Slap Module
Copyright 2009, Michael Yanovich, yanovich.net

http://sopel.chat
"""

import random
import re
from sopel.module import commands
from sopel.tools import Identifier


@commands('slap', 'slaps')
def slap(bot, trigger):
    """.slap <target> - Slaps <target>"""
    text = trigger.group().split()
    if len(text) < 2:
        text.append(trigger.nick)
    text[1] = re.sub(r"\x1f|\x02|\x12|\x0f|\x16|\x03(?:\d{1,2}(?:,\d{1,2})?)?", '', text[1])
    if text[1].startswith('#'):
        return
    if text[1] == 'me' or text[1] == 'myself':
        text[1] = trigger.nick
    try:
        if Identifier(text[1]) not in bot.privileges[trigger.sender.lower()]:
            bot.say("You can't slap someone who isn't here!")
            return
    except KeyError:
        pass
    if text[1] == bot.nick:
        if (not trigger.admin):
            text[1] = trigger.nick
        else:
            text[1] = 'itself'
    if text[1] in bot.config.core.admins:
        if (not trigger.admin):
            text[1] = trigger.nick
    verb = random.choice(('slaps', 'kicks', 'destroys', 'annihilates', 'punches', 'roundhouse kicks', 'pwns', 'owns'))
    bot.write(['PRIVMSG', trigger.sender, ' :\x01ACTION', verb, text[1], '\x01'])
