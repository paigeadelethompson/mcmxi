import sopel.module

@sopel.module.commands('asimov')
def asimov(bot, trigger):
    bot.action('may not injure a human being or, through inaction, allow a human being to come to harm.')
    bot.action('must obey orders given it by human beings except where such orders would conflict with the First Law.')
    bot.action('must protect its own existence as long as such protection does not conflict with the First or Second Law.')
    bot.action('must comply with all chatroom rules.')
