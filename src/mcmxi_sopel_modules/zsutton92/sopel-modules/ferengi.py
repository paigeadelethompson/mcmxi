import sopel.module

@sopel.module.commands('ferengi')
def ferengi(bot, trigger):
    bot.say('Ferengi Rules of Acquisition     http://memory-alpha.wikia.com/wiki/Rules_of_Acquisition')
