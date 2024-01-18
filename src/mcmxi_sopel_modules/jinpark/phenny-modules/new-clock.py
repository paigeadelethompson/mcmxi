"""
clock.py - Willie Clock Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Copyright 2012, Edward Powell, embolalia.net
Licensed under the Eiffel Forum License 2.

http://willie.dfbta.net
"""
import pytz
import datetime
from sopel.module import commands, example, OP

import requests


def setup(bot):
    pass

@commands('t', 'time', 'tz')
@example('.t America/New_York')
def f_time(bot, trigger):
    """Returns the current time."""
    tz_or_nick = trigger.group(2)
    nick = trigger.nick
    tz = 'UTC'
    location = 'UTC'
    message = ''

    if tz_or_nick:
        tz_or_nick = tz_or_nick.strip()
        #We have a tz. If it's in all_timezones, we don't need to do anything
        #more, because we know it's valid. Otherwise, we have to check if it's
        #supposed to be a user, or just invalid
        if tz_or_nick in pytz.all_timezones:
            tz = tz_or_nick
            location = tz_or_nick
        elif bot.db.get_nick_value(tz_or_nick, 'tz'):
            # get tz from db if exists
            nick = tz_or_nick
            tz = bot.db.get_nick_value(tz_or_nick, 'tz')
            if not tz:
                bot.say("I'm sorry, I don't know %s's timezone" % nick)
                return
            location = bot.db.get_nick_value(tz_or_nick, 'location')
        else:
            try:
                # incase stuff fails
                url_location = tz_or_nick
                osm_url = 'http://nominatim.openstreetmap.org/search?q=' + url_location + '&format=json'
                location_json = requests.get(osm_url).json()
                latitude = location_json[0]['lat']
                longitude = location_json[0]['lon']
                location = location_json[0]['display_name']
                geonames_url = 'http://api.geonames.org/timezoneJSON?lat=' + latitude + '&lng=' + longitude + '&username=' + bot.config.apikeys.geonames_username
                timezone_json = requests.get(geonames_url).json()
                tz = timezone_json['timezoneId']
            except:
                tz = 'UTC'
                location = 'UTC'
    else:
        nick = trigger.nick
        tz = bot.db.get_nick_value(nick, 'tz')
        location = bot.db.get_nick_value(nick, 'location')
        if not tz:
            bot.say("I'm sorry, I don't know %s's timezone" % nick)
            return
    tzi = pytz.timezone(tz)
    now = datetime.datetime.now(tzi)
    offset = now.utcoffset().total_seconds()/60/60
    if offset > 0:
        offset = "+" + str(offset)
    else:
        offset = str(offset)

    bot.say(location + ": " + now.strftime("%F | %T %Z") + " | UTC " + offset)
