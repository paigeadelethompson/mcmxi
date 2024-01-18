# coding=utf-8
"""
memo.py - Sopel Memo Module
Copyright 2016, Natalie Fearnley

http://sopel.chat
"""
from __future__ import unicode_literals, absolute_import, print_function, division

import os
import time
import threading
import sys
from sopel.tools import Identifier, iterkeys
from sopel.tools.time import get_timezone, format_time
from sopel.module import commands, nickname_commands, rule, priority, example, require_admin

def loadMemories(fn, lock):
    lock.acquire()
    try:
        result = {}
        f = open(fn)
        for line in f:
            line = line.strip()
            if sys.version_info.major < 3:
                line = line.decode('utf-8')
            if line:
                try:
                    keyword, message = line.split('\t', 1)
                except ValueError:
                    continue
                result[keyword] = message;
        f.close()
    finally:
        lock.release()
    return result

def dumpMemories(fn, data, lock):
    lock.acquire()
    try:
        f = open(fn, 'w')
        for keyword in iterkeys(data):
            message = data[keyword]
            line = '\t'.join((keyword, message))
            try:
                to_write = line + '\n'
                if sys.version_info.major < 3:
                    to_write = to_write.encode('utf-8')
                f.write(to_write)
            except IOError:
                break
        try:
            f.close()
        except IOError:
            pass
    finally:
        lock.release()
    return True

def setup(self):
    fn = self.nick + '-' + self.config.core.host + '.memo.db'
    self.memo_filename = os.path.join(self.config.core.homedir, fn)
    if not os.path.exists(self.memo_filename):
        try:
            f = open(self.memo_filename, 'w')
        except OSError:
            pass
        else:
            f.write('')
            f.close()
    self.memory['memo_lock'] = threading.Lock()
    self.memory['memories'] = loadMemories(self.memo_filename, self.memory['memo_lock'])

@require_admin
@commands('memorize', 'memorise', 'memo', 'remember')
@example('.memorize lucky You\'ve got to ask yourself one question. Do I feel lucky? Well, do ya, punk?')
def memorize(bot, trigger):
    if not trigger.group(4):
        bot.reply("Memorize what?")
        return
    
    keyword = trigger.group(3)
    message = trigger.group(2).lstrip(keyword).lstrip()
    
    if not os.path.exists(bot.memo_filename):
        return
    
    bot.memory['memo_lock'].acquire()
    try:
        bot.memory['memories'][keyword] = message
    finally:
        bot.memory['memo_lock'].release()
        
    bot.reply("I'll remember %s." % keyword)
    
    dumpMemories(bot.memo_filename, bot.memory['memories'], bot.memory['memo_lock'])

@commands('recall')
def recall(bot, trigger):
    if not trigger.group(3):
        bot.reply("Recall what?")
        return
    
    keyword = trigger.group(3)

    bot.memory['memo_lock'].acquire()
    try:
        message = bot.memory['memories'].get(keyword)            
    finally:
        bot.memory['memo_lock'].release()
    
    if not message:
        bot.reply("I don't remember %s." % keyword)
        return
    
    bot.say("%s: %s" % (keyword, message))

@require_admin
@commands('forget')
def forget(bot, trigger):
    if not trigger.group(3):
        bot.reply("Forget what?")
        return
    
    keyword = trigger.group(3)

    if not os.path.exists(bot.memo_filename):
        return

    bot.memory['memo_lock'].acquire()
    try:
        message = bot.memory['memories'].pop(keyword, None)
    finally:
        bot.memory['memo_lock'].release()
    
    if not message:
        bot.reply("I don't remember %s." % keyword)
        return
    
    bot.reply("I'll forget %s." % keyword)

    dumpMemories(bot.memo_filename, bot.memory['memories'], bot.memory['memo_lock'])
