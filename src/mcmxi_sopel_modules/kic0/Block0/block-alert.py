import sopel.module
import requests
import re
import time

PERIOD=60

@sopel.module.interval(PERIOD)
def Bloc0(bot):
  try:
    r=requests.get('https://pool.xmr.pt/api/pool/stats')
    j=r.json()
  except Exception,e:
    bot.say("Red Alert! Red Alert! The pools API is unreachable !","YOURIRCNICK")
  try:
    blocktime=j['pool_statistics']['lastBlockFoundTime']
    timestamp = int(time.time())
    if (timestamp-blocktime) < 60 :
      bot.say(u"Block!!!! BLOOOCCCCKKK!!!! \o/ https://imgur.com/a/xxBbX","#yourchan")
  except:
     pass

