##
## Trigger commands to interact with pools API
## .last - info on last mined block
## .status - info on pool statistics
## .effort - if only effort gives current round effort if a X string is given it will give the average effort on last X number of blocks 
## .stats - Gives miner info for given wallet address mining on the pool
##
## Thanks to bitmoeda and notmike for the help
##
import sopel.module
import requests
import re
import time

def seconds_to_date(seconds_ago):
    minutes_ago, seconds_ago = divmod(seconds_ago, 60)
    hours_ago, minutes_ago = divmod(minutes_ago, 60)
    days_ago, hours_ago = divmod(hours_ago, 24)
#   weeks_ago, days_ago = divmod(days_ago, 7)
    return [seconds_ago, minutes_ago, hours_ago, days_ago]

@sopel.module.commands('last')
def last(bot, trigger):
  try:
    r = requests.get('https://pool.xmr.pt/api/pool/blocks')
    j = r.json()
  except Exception,e:
    pass
  try:
    ts = j[0]['ts']/1000
    seconds_ago = int(time.time()-ts)
    diff = j[0]['diff']
    shares = j[0]['shares']
    value = j[0]['value']/1E12
    effort = shares*100/diff
    [seconds_ago, minutes_ago, hours_ago, days_ago] = seconds_to_date(seconds_ago)
    bot.say("The last block was mined {0} days, {1} hours and {2} minutes. The difficulty was {4}, {5} shares were needed, and had a reward of {6} with {7}% effort ".format(days_ago, hours_ago, minutes_ago, seconds_ago, diff, shares, value, effort))
  except:
    bot.say("The Pool API is unreachable!")


@sopel.module.commands('status')
def status(bot, trigger):
  try:
    r=requests.get('https://pool.xmr.pt/api/pool/stats')
    j=r.json()
    rn=requests.get('https://pool.xmr.pt/api/network/stats')
    jn=rn.json()
    hashrate=j['pool_statistics']['hashRate']
    miners=j['pool_statistics']['miners']
    blocks=j['pool_statistics']['totalBlocksFound']
    netdiff=jn['difficulty']
    blocktime= netdiff / hashrate / 3600
    days = blocktime / 24
    hours = blocktime % 24
    timetext="Time between blocks is {0} days and {1} hours.".format(days, hours)
    khrate= hashrate / 1000
    bot.say("The hashrate is {0} KH/s, there are {1} miners and we've mined {2} blocks. {3}".format(khrate, miners, blocks, timetext))
  except:
    bot.say("The Pool API is unreachable!")

@sopel.module.commands('effort')
def effort(bot, trigger):
    if trigger.group(2) == None:
        r = requests.get('https://pool.xmr.pt/api/network/stats')
        j = r.json()
        rn = requests.get('https://pool.xmr.pt/api/pool/stats')
        jn = rn.json()
        diff = j['difficulty']
        roundHashes = jn['pool_statistics']['roundHashes']
        effort = 100*roundHashes/diff
        bot.say("We're at {0}% effort in the actual round".format(effort))
    else:
        N = trigger.group(2)
        blockrequest = 'https://pool.xmr.pt/api/pool/blocks?limit={0}'.format(N)
        r = requests.get(blockrequest)
        j = r.json()
        effort = 0
        for i in range (0, int(N)):
                shares = j[i]['shares']
                diff = j[i]['diff']
                effort += (100*shares/diff)
        try:
                effort = (effort/int(N))
                bot.say("We're at {0}% effort in the last {1} blocks".format(effort, N))
        except:
                r = requests.get('https://pool.xmr.pt/api/pool/stats')
                j = r.json()
                blocks = j['pool_statistics']['totalBlocksFound']
                bot.say("The pool has mined {0} blocks total".format(blocks))

@sopel.module.commands('stats')
def stats(bot, trigger):
    if trigger.group(2) == None:
        bot.say("Please insert your mining Address")
    else:
        try:
            wallet = trigger.group(2)
            r=requests.get('https://pool.xmr.pt/api/miner/' + wallet + '/stats')
            j=r.json()
            hashrate=j['hash']
            due=j['amtDue'] / 1E12
            paid=j['amtPaid'] /1E12
            bot.say("Your Stats are: Hashrate {0} H/s you have {1}XMR due and you were already paid {2}XMR".format(hashrate, due, paid))
        except:
            bot.say("Invalid wallet Address!")

