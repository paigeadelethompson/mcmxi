import sopel.module

@sopel.module.commands('packt')
def packt(bot, trigger):
    bot.say('Packt Free Book (daily)     https://www.packtpub.com/packt/offers/free-learning')
