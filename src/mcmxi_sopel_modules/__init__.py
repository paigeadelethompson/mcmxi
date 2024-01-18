"""mcmxi_sopel_modules

vendor module for unmanaged Sopel modules
"""
from __future__ import unicode_literals, absolute_import, division, print_function

from sopel import plugin

try:
    from mcmxi_sopel_modules.cottongin.sopel_modules.exchange import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.figlet import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.gas import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.hueg import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.misc import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.nhl import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.odds import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.podcasts import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.soma import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.space import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.spongebob import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.twitch import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.twitter import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.urbandictionary import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.vimeo import *
    from mcmxi_sopel_modules.cottongin.sopel_modules.wolfram import *
except Exception as e:
    print(e)

try:
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.anilist import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.anime import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.animerss import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.bday import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.dubtrack import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.edict import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.egs import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.fact import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.gdq import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.gelbooru import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.heh import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.hltb import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.hn import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.hots import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.instagram import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.knowyourmeme import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.mahjong import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.mal import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.mtg import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.pb import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.pixiv import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.ps import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.ratewaifu import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.search2 import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.shadowverse import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.smug import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.steam import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.stocks import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.sync import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.traffic import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.twitch import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.twitter import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.urbandict import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.wafflebot import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.wait import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.weather2 import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.wemo import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.worldcup import *
    from mcmxi_sopel_modules.dasu.syrup_sopel_modules.ygo import *
except Exception as e:
    print(e)

try:
    from mcmxi_sopel_modules.jinpark.phenny_modules.aftership import *
    from mcmxi_sopel_modules.jinpark.phenny_modules.alphavantage import *
    from mcmxi_sopel_modules.jinpark.phenny_modules.bobkov import *
    from mcmxi_sopel_modules.jinpark.phenny_modules.crypto import *
    from mcmxi_sopel_modules.jinpark.phenny_modules.giphy import *
    from mcmxi_sopel_modules.jinpark.phenny_modules.jargon import *
    from mcmxi_sopel_modules.jinpark.phenny_modules.jisho import *
    from mcmxi_sopel_modules.jinpark.phenny_modules.stocks import *
    from mcmxi_sopel_modules.jinpark.phenny_modules.urbandictionary import *
    from mcmxi_sopel_modules.jinpark.phenny_modules.voice_join import *
except Exception as e:
    print(e)

try:
    from mcmxi_sopel_modules.pilate.sopel_modules.bitfinex import *
    from mcmxi_sopel_modules.pilate.sopel_modules.bithumb import *
    from mcmxi_sopel_modules.pilate.sopel_modules.bitstamp import *
    from mcmxi_sopel_modules.pilate.sopel_modules.calc import *
    from mcmxi_sopel_modules.pilate.sopel_modules.coinbase import *
    from mcmxi_sopel_modules.pilate.sopel_modules.finance import *
    from mcmxi_sopel_modules.pilate.sopel_modules.findtime import *
    from mcmxi_sopel_modules.pilate.sopel_modules.quakes import *
    from mcmxi_sopel_modules.pilate.sopel_modules.rockets import *
    from mcmxi_sopel_modules.pilate.sopel_modules.sports import *
    from mcmxi_sopel_modules.pilate.sopel_modules.twits import *
    from mcmxi_sopel_modules.pilate.sopel_modules.ud import *
except Exception as e:
    print(e)

try:
    from mcmxi_sopel_modules.pixelguff.ultrabutt.bgmarkov import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.canary import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.dd import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.douchebags import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.elizabot import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.fart import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.fuckedreport import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.fuckerreport import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.goog import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.lookup import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.mingeburger import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.randomword import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.sexwee import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.testes import *
    from mcmxi_sopel_modules.pixelguff.ultrabutt.wash import *
except Exception as e:
    print(e)

try:
    from mcmxi_sopel_modules.russellb.sopelmods.actions import *
    from mcmxi_sopel_modules.russellb.sopelmods.cowsay import *
    from mcmxi_sopel_modules.russellb.sopelmods.dance import *
    from mcmxi_sopel_modules.russellb.sopelmods.devexcuse import *
    from mcmxi_sopel_modules.russellb.sopelmods.figlet import *
    from mcmxi_sopel_modules.russellb.sopelmods.ipv6 import *
    from mcmxi_sopel_modules.russellb.sopelmods.pyjoke import *
    from mcmxi_sopel_modules.russellb.sopelmods.stock import *
    from mcmxi_sopel_modules.russellb.sopelmods.text import *
    from mcmxi_sopel_modules.russellb.sopelmods.wunderground import *
except Exception as e:
    print(e)

try:
    from mcmxi_sopel_modules.sopel_irc.sopel_extras.bomb import *
    from mcmxi_sopel_modules.sopel_irc.sopel_extras.document import *
    from mcmxi_sopel_modules.sopel_irc.sopel_extras.helpbot import *
    from mcmxi_sopel_modules.sopel_irc.sopel_extras.multimessage import *
    from mcmxi_sopel_modules.sopel_irc.sopel_extras.roulette import *
    from mcmxi_sopel_modules.sopel_irc.sopel_extras.slap import *
    from mcmxi_sopel_modules.sopel_irc.sopel_extras.whois import *
except Exception as e:
    print(e)

try:
    from mcmxi_sopel_modules.nc.adderall.adderall import *
except Exception as e:
    print(e)
