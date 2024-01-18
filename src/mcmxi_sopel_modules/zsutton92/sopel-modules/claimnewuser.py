import sopel.module

@sopel.module.commands('pee')
def pee(bot, trigger):
    bot.say(trigger.nick + ' urinates on new user! Claimed!')
