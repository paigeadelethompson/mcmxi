import sopel.module

@sopel.module.commands('meraki')
def meraki(bot, trigger):
    bot.say('MX     https://meraki.cisco.com/tc/freemx')
    bot.say('Switch     https://meraki.cisco.com/tc/freeswitch')
    bot.say('AP     https://meraki.cisco.com/tc/freeap')
