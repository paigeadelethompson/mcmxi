##
## These are mostly taken from our beloved monerobux thanks to jwinterm
## https://github.com/jwinterm/monerobux/blob/master/network.py
##
import sopel.module
import requests
import re

networkurl = "http://node.xmr.pt:18081/getinfo"

@sopel.module.commands('fork', 'garfoduro')
def fork(bot, trigger):
  try:
    r=requests.get(networkurl)
    j=r.json()
  except Exception,e:
    pass
  try:
    height=j["height"]
##insert next fork height here
    forkheight=1788000
    if forkheight > height:
      bot.say("The current block height is {0:,}. Fork height is {1:,}. {2:,} blocks to go, happening in approximately {3:.2f} hours.".format(height,forkheight,forkheight-height,(forkheight-height)/30.0))
    else:
      bot.say("I don't know when the next fork is.")
  except:
    bot.say("Something borked -_-")

@sopel.module.commands('network')
def network(bot, trigger):
  try:
    r=requests.get(networkurl)
    j=r.json()
  except Exception,e:
    pass
  try:
    height=j["height"]
    diff=j["difficulty"]
    hashrate=float(diff)/120
    bot.say("The current block height is {0:,}. Difficulty is {1:,}. Hashrate is {2:.2f} Mh/s.".format(height,diff,hashrate/1e6))
  except:
    bot.say("Something borked -_-")

@sopel.module.commands('mempool')
def mempool(bot, trigger):
  try:
    r=requests.get(networkurl)
    j=r.json()
    bot.say("The current number of txs in Monero's mempool is {0}".format(j['tx_pool_size']))
  except:
    bot.say("Something borked o_O")

@sopel.module.commands('blocksize')
def blocksize(bot, trigger):
  try:
    r=requests.get(networkurl)
    j=r.json()
  except Exception,e:
    pass
  try:
    bot.say("Median blocksize over last 200 blocks is {0} bytes".format(j['block_size_median']))
  except:
    bot.say("Bomething sorked 0_0")

@sopel.module.commands('mine')
def mine(bot, trigger):
  try: 
    r=requests.get('https://pool.xmr.pt/api/network/stats')
    j=r.json()
    diff=float(j['difficulty'])
    value=float(j['value'])/1e12
    hashrate=float(trigger.group(2))
    xmrperday=(hashrate/(diff/120))*720*value
    bot.say("At {:.0f} h/s with network diff of {:.2e} and block reward {:.2f} you can expect {:.4f} XMR per day.".format(hashrate, diff, value, xmrperday))
  except:
    bot.say("Mining is for suckers.")

@sopel.module.commands('solo')
def solo(bot, trigger):
  try: 
    r=requests.get('https://pool.xmr.pt/api/network/stats')
    j=r.json()
    diff=float(j['difficulty'])
    hashrate=float(trigger.group(2))
    timetoblock=(diff/hashrate)
    bot.say("At {:.0f} h/s with network diff of {:.2e} your expected time for find a block is {:.2e} s or {:.2f} days.".format(hashrate, diff, timetoblock, timetoblock/(60*60*24)))
  except:
    bot.say("Mining is for suckers.")

