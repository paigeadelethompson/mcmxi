# -*- coding: utf-8 -*-

from random import choice
import time
from sopel import module

def rules(bot, input):
    bot.say('Chat Rules:     https://pastebin.com/Vrq9bHBD')
rules.commands = ['rules']

def rules1(bot, input):
    bot.say('The channel operators are not Spiceworks employees, and currently in no way related to Spiceworks, Inc. Some Spiceworks employees do however hang out in the channel but this is no reason to harass them.')
rules1.commands = ['rules1']

def rules2(bot, input):
    bot.say('You are expected to treat people as if they are human. Failing to do so will result in us banning you or telling your mother.')
rules2.commands = ['rules2']

def rules3(bot, input):
    bot.say('Swearing and profanities are allowed. Direct insults, trolling or being a jackass will get you kicked and/or banned. This is a subjective matter and decisions made by the operators are not up for debate. We don't kick often and ban rarely at best, so don't be that special kind of stupid.')
rules3.commands = ['rules3']

def rules4(bot, input):
    bot.say('If someone's out of line in channel, call them on it. If it continues, hail one of the ops. If someone's annoying you in PMs, make liberal use of the /ignore command and notify Freenode staff. (see http://freenode.net/faq.shtml#helpfromstaff)')
rules4.commands = ['rules4']

def rules5(bot, input):
    bot.say('If no ops are available during times of distress don't hesitate to PM them, many have notifications enabled.')
rules5.commands = ['rules5']
            
def rules6(bot, input):
    bot.say('Thou shalt not flood, spam or troll.')
rules6.commands = ['rules6']
            
def rules7(bot, input):
    bot.say('Flooding is 3 times identical lines or over, or a short burst of 5 or more lines. There's no autokick but ops will dislike you. Please use Pastebin or the like for multiline pasts. Others will be considered as flood.')
rules7.commands = ['rules7']
            
def rules8(bot, input):
    bot.say('Use of long links, caps and colors is allowed, though none are allowed as a constant gimmick in the interest of keeping things nice and clean.')
rules8.commands = ['rules8']
            
def rules9(bot, input):
    bot.say('If your client, connection or freenode link decide to become uunstable and start shouting joins and quits into the channel while you are away we will kick and, if needed, ban you. A notification to anyone with power that your problems are over will get you back in. Your will probably have a PM waiting telling you this, too.')
rules9.commands = ['rules9']
            
def rules10(bot, input):
    bot.say('Please ask before activating a bot or auto-responder in channel.')
rules10.commands = ['rules10']
            
def rules11(bot, input):
    bot.say('Please flag potentially NSFW links as NSFW.')
rules11.commands = ['rules11']
            
def rules12(bot, input):
    bot.say('Mind what you share online. Be careful not to post personal info or company proprietary information.')
rules12.commands = ['rules12']
            
def rules13(bot, input):
    bot.say('Please don't dox. We already have people for that.')
rules13.commands = ['rules13']
            
def rules14(bot, input):
    bot.say('Minecraft stuff belongs in #spicecraft.')
rules14.commands = ['rules14']
