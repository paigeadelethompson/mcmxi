# coding=utf-8
"""
debug.py - Sopel Debugging Module
Copyright 2013, Dimitri "Tyrope" Molenaars, Tyrope.nl
Licensed under the Eiffel Forum License 2.

http://sopel.chat
"""

from sopel.module import commands, example

@commands('privs')
@example('.privs', '.privs #channel')
def privileges(bot, trigger):
    """Print the privileges of a specific channel, or the entire array."""
    if trigger.group(2):
        try:
            bot.say(str(bot.privileges[trigger.group(2)]))
        except Exception:
            bot.say("Channel not found.")
    else:
        bot.say(str(bot.privileges))

@commands('admins')
@example('.admins')
def admins(bot, trigger):
    """Print the list of admins, including the owner."""
    owner = bot.config.core.owner
    admins = str(bot.config.core.get_list('admins'))
    bot.say("[Owner]"+owner+" [Admins]"+admins)

@commands('debug_print')
@example('.debug_print')
def debug_print(bot, trigger):
    """Calls version, admins and privileges prints in sequence."""
    try:
        sopel.modules.version.version(bot, trigger)
    except Exception as e:
        bot.say('An error occurred trying to get the current version.')
    admins(bot, trigger)
    privileges(bot, trigger)

@commands('raiseException', 'causeProblems', 'giveError')
@example('.raiseException')
def cause_problems(bot, trigger):
    """This deliberately causes sopel to raise exceptional problems."""
    raise Exception("Problems were caused on command.")

