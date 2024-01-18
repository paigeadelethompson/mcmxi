# -*- coding: utf8 -*-
"""
weather.py - Willie Yahoo! Weather Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright 2012, Edward Powell, embolalia.net
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
# NOTE: delete wea, and wf code later

from sopel import web
from sopel.module import commands, example

from datetime import datetime
import feedparser
from lxml import etree
import requests
import pytz
import geocoder

degc = "\xb0C"
degf = "\xb0F"
bold = "\x02"
forc = ['f','F','c','C']

AQI_SEARCH_URL = "http://api.waqi.info/search/?token={}&keyword={}"

def degreeToDirection(deg):
  if (337.5 <= deg <= 360) or (0 <= deg < 22.5):
    return "N"
  elif 22.5 <= deg < 67.5:
    return "NE"
  elif 67.5 <= deg < 112.6:
    return "E"
  elif 112.6 <= deg < 157.5:
    return "SE"
  elif 157.5 <= deg < 202.5:
    return "S"
  elif 202.5 <= deg < 247.5:
    return "SW"
  elif 247.5 <= deg < 292.5:
    return "W"
  elif 292.5 <= deg < 337.5:
    return "NW"

def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%m/%d')


def setup(bot):
    pass

def woeid_search(query):
    """
    Find the first Where On Earth ID for the given query. Result is the etree
    node for the result, so that location data can still be retrieved. Returns
    None if there is no result, or the woeid field is empty.
    """
    # query = urllib.urlencode({'q': 'select * from geo.placefinder where text="%s"' % query})
    # body = web.get('http://query.yahooapis.com/v1/public/yql?' + query)
    payload = {'q': 'select * from geo.places(1) where text="%s"' % query, 'format': 'json'}
    body = requests.get('http://query.yahooapis.com/v1/public/yql?', params=payload)
    parsed = body.json()
    first_result = parsed['query']['results']
    if first_result is None or len(first_result) == 0:
        return None
    return first_result

def geocoder_search(bot, location_name):
    geocoded = geocoder.bing(location_name, key=bot.config.apikeys.bing_maps_key)
    return geocoded.json

def aqicn_uid_search(bot, location):
    key = bot.config.apikeys.aqicn_key
    search = requests.get(AQI_SEARCH_URL.format(key, location)).json()
    if len(search["data"]) > 0:
        uid = search["data"][0]["uid"]
        name = search["data"][0]["station"]["name"]
        return uid, name
    return None, None

def get_cover(parsed):
    try:
        condition = parsed.entries[0]['yweather_condition']
    except KeyError:
        return 'unknown'
    text = condition['text']
    # code = int(condition['code'])
    # TODO parse code to get those little icon thingies.
    return text


def get_temp(parsed):
    try:
        condition = parsed.entries[0]['yweather_condition']
    except KeyError:
        return 'unknown'
    temp = int(condition['temp'])
    f = round((temp * 1.8) + 32, 2)
    return ('%d\u00B0C (%d\u00B0F)' % (temp, f))


def get_pressure(parsed):
    try:
        pressure = parsed['feed']['yweather_atmosphere']['pressure']
    except KeyError:
        return 'unknown'
    millibar = float(pressure)
    inches = int(millibar / 33.7685)
    return ('%din (%dmb)' % (inches, int(millibar)))


def convert_unixtime_to_local(unixtime, timezone):
    tz = pytz.timezone(timezone)
    localtime = datetime.fromtimestamp(unixtime, pytz.utc).astimezone(tz)
    return localtime.strftime("%H:%M:%S")


def get_wind(parsed):
    try:
        wind_data = parsed['feed']['yweather_wind']
    except KeyError:
        return 'unknown'
    try:
        kph = float(wind_data['speed'])
    except ValueError:
        kph = -1
        # Incoming data isn't a number, default to zero.
        # This is a dirty fix for issue #218
    speed = int(round(kph / 1.852, 0))
    degrees = int(wind_data['direction'])
    if speed < 1:
        description = 'Calm'
    elif speed < 4:
        description = 'Light air'
    elif speed < 7:
        description = 'Light breeze'
    elif speed < 11:
        description = 'Gentle breeze'
    elif speed < 16:
        description = 'Moderate breeze'
    elif speed < 22:
        description = 'Fresh breeze'
    elif speed < 28:
        description = 'Strong breeze'
    elif speed < 34:
        description = 'Near gale'
    elif speed < 41:
        description = 'Gale'
    elif speed < 48:
        description = 'Strong gale'
    elif speed < 56:
        description = 'Storm'
    elif speed < 64:
        description = 'Violent storm'
    else:
        description = 'Hurricane'

    if (degrees <= 22.5) or (degrees > 337.5):
        degrees = '\u2191'
    elif (degrees > 22.5) and (degrees <= 67.5):
        degrees = '\u2197'
    elif (degrees > 67.5) and (degrees <= 112.5):
        degrees = '\u2192'
    elif (degrees > 112.5) and (degrees <= 157.5):
        degrees = '\u2198'
    elif (degrees > 157.5) and (degrees <= 202.5):
        degrees = '\u2193'
    elif (degrees > 202.5) and (degrees <= 247.5):
        degrees = '\u2199'
    elif (degrees > 247.5) and (degrees <= 292.5):
        degrees = '\u2190'
    elif (degrees > 292.5) and (degrees <= 337.5):
        degrees = '\u2196'

    return description + ' ' + str(speed) + 'kt (' + degrees + ')'


# @commands('weather', 'wea')
# @example('.weather London')
def weather(bot, trigger):
    """.weather location - Show the weather at the given location."""
    location = trigger.group(2)
    try:
        location = trigger.group(2).lower()
    except:
        location = ''
    woeid = ''
    nick = trigger.nick.lower()
    if not location:
        woeid = bot.db.get_nick_value(nick, 'woeid')
        latitude = bot.db.get_nick_value(nick, 'latitude')
        longitude = bot.db.get_nick_value(nick, 'longitude')
        location = bot.db.get_nick_value(nick, 'location')
        if not woeid:
            return bot.msg(trigger.sender, "I don't know where you live. " +
                           'Give me a location, like .weather London, or tell me where you live by saying .setlocation London, for example.')
    else:
        location = location.strip()
        if bot.db.get_nick_value(location, 'woeid'):
            nick = location
            woeid = bot.db.get_nick_value(nick, 'woeid')
            latitude = bot.db.get_nick_value(nick, 'latitude')
            longitude = bot.db.get_nick_value(nick, 'longitude')
            location = bot.db.get_nick_value(nick, 'location')
            if not woeid:
                return bot.msg(trigger.sender, "I don't know who this is or they don't have their location set.")
        else: 
            # first_result = woeid_search(location)
            result = geocoder_search(bot, location)
            if result["status"] is 'OK':
                woeid = result['address']
                latitude = result['lat']
                longitude = result['lng']
                location = result['address']

    if not woeid:
        return bot.reply("I don't know where that is.")
    wea_text = weabase(bot, latitude, longitude, location)
    bot.say(wea_text)

    # query = web.urlencode({'w': woeid, 'u': 'c'})
    # url = 'http://weather.yahooapis.com/forecastrss?' + query
    # parsed = feedparser.parse(url)
    # location = parsed['feed']['title']

    # cover = get_cover(parsed)
    # temp = get_temp(parsed)
    # pressure = get_pressure(parsed)
    # wind = get_wind(parsed)
    # bot.say(u'%s: %s, %s, %s, %s' % (location, cover, temp, pressure, wind))


# @commands('wf', 'forecast')
# @example('.wf London')
def weather_forecast(bot, trigger):
    """.weather location - Show the weather at the given location."""

    location = trigger.group(2)
    try:
        location = trigger.group(2).lower()
    except:
        location = ''
    woeid = ''
    units = 'si'
    nick = trigger.nick.lower()
    if not location:
        woeid = bot.db.get_nick_value(nick, 'woeid')
        latitude = bot.db.get_nick_value(nick, 'latitude')
        longitude = bot.db.get_nick_value(nick, 'longitude')
        location = bot.db.get_nick_value(nick, 'location')
        if not woeid:
            return bot.msg(trigger.sender, "I don't know where you live. " +
                           'Give me a location, like .weather London, or tell me where you live by saying .setlocation London, for example.')
    else:
        location = location.strip()
        if bot.db.get_nick_value(location, 'woeid'):
            nick = location
            woeid = bot.db.get_nick_value(nick, 'woeid')
            latitude = bot.db.get_nick_value(nick, 'latitude')
            longitude = bot.db.get_nick_value(nick, 'longitude')
            location = bot.db.get_nick_value(nick, 'location')
            if not woeid:
                return bot.msg(trigger.sender, "I don't know who this is or they don't have their location set.")
        else: 
            # first_result = woeid_search(location)
            # if first_result is not None:
            #     woeid = first_result['place']['woeid']
            #     latitude = first_result['place']['centroid']['latitude']
            #     longitude = first_result['place']['centroid']['longitude']
            #     location = first_result['place']['name']
            result = geocoder_search(bot, location)
            if result["status"] is 'OK':
                woeid = result['address']
                latitude = result['lat']
                longitude = result['lng']
                location = result['address']
                units = 'si'

    if not woeid:
        return bot.reply("I don't know where that is.")

    wf_text = wfbase(bot, latitude, longitude, location, units)
    bot.say(wf_text)

# @commands('wc', 'wf', 'forecast', 'weather', 'wea')
# @example('.wc London')
def weather_combined(bot, trigger):
    """.wc location - Show the weather and forecast at the given location."""

    location = trigger.group(2)
    try:
        location = trigger.group(2).lower()
    except:
        location = ''
    woeid = ''
    units = 'si'
    nick = trigger.nick.lower()
    if not location:
        woeid = bot.db.get_nick_value(nick, 'woeid')
        latitude = bot.db.get_nick_value(nick, 'latitude')
        longitude = bot.db.get_nick_value(nick, 'longitude')
        location = bot.db.get_nick_value(nick, 'location')
        if not woeid:
            return bot.msg(trigger.sender, "I don't know where you live. " +
                           'Give me a location, like .weather London, or tell me where you live by saying .setlocation London, for example.')
    else:
        location = location.strip()
        if bot.db.get_nick_value(location, 'woeid'):
            nick = location
            woeid = bot.db.get_nick_value(nick, 'woeid')
            latitude = bot.db.get_nick_value(nick, 'latitude')
            longitude = bot.db.get_nick_value(nick, 'longitude')
            location = bot.db.get_nick_value(nick, 'location')
            if not woeid:
                return bot.msg(trigger.sender, "I don't know who this is or they don't have their location set.")
        else: 
            # first_result = woeid_search(location)
            # if first_result is not None:
            #     woeid = first_result['place']['woeid']
            #     latitude = first_result['place']['centroid']['latitude']
            #     longitude = first_result['place']['centroid']['longitude']
            #     location = first_result['place']['name']
            result = geocoder_search(bot, location)
            if result["status"] is 'OK':
                woeid = result['address']
                latitude = result['lat']
                longitude = result['lng']
                location = result['address']
                units = 'si'

    if not woeid:
        return bot.reply("I don't know where that is.")

    wc_text = wcbase(bot, latitude, longitude, location, units)
    bot.say(wc_text)

# @commands('w5', 'wd')
# @example('.w5 London')
def weather_five_days(bot, trigger):
    """.w5 location - Show the weather forecast at the given location for the next 4 days."""

    location = trigger.group(2)
    try:
        location = trigger.group(2).lower()
    except:
        location = ''
    woeid = ''
    units = 'si'
    nick = trigger.nick.lower()
    if not location:
        woeid = bot.db.get_nick_value(nick, 'woeid')
        latitude = bot.db.get_nick_value(nick, 'latitude')
        longitude = bot.db.get_nick_value(nick, 'longitude')
        location = bot.db.get_nick_value(nick, 'location')
        if not woeid:
            return bot.msg(trigger.sender, "I don't know where you live. " +
                           'Give me a location, like .weather London, or tell me where you live by saying .setlocation London, for example.')
    else:
        location = location.strip()
        if bot.db.get_nick_value(location, 'woeid'):
            nick = location
            woeid = bot.db.get_nick_value(nick, 'woeid')
            latitude = bot.db.get_nick_value(nick, 'latitude')
            longitude = bot.db.get_nick_value(nick, 'longitude')
            location = bot.db.get_nick_value(nick, 'location')
            if not woeid:
                return bot.msg(trigger.sender, "I don't know who this is or they don't have their location set.")
        else: 
            # first_result = woeid_search(location)
            # if first_result is not None:
            #     woeid = first_result['place']['woeid']
            #     latitude = first_result['place']['centroid']['latitude']
            #     longitude = first_result['place']['centroid']['longitude']
            #     location = first_result['place']['name']
            result = geocoder_search(bot, location)
            if result["status"] is 'OK':
                woeid = result['address']
                latitude = result['lat']
                longitude = result['lng']
                location = result['address']
                units = 'si'

    if not woeid:
        return bot.reply("I don't know where that is.")

    w5_text = w5base(bot, latitude, longitude, location, units)
    bot.say(w5_text)

# @commands('setlocation', 'setloc')
# @example('.setlocation Columbus, OH')
def update_woeid(bot, trigger):
    """Set your default weather location."""
    if bot.db:
        nick = trigger.nick.lower()
        location = trigger.group(2)
        # if first_result is None:
        #     return bot.reply("I don't know where that is.")

        # woeid = first_result['place']['woeid']
        # latitude = first_result['place']['centroid']['latitude']
        # longitude = first_result['place']['centroid']['longitude']
        # location = first_result['place']['name']
        # timezone = first_result['place']['timezone']['content']
        result = geocoder_search(bot, location)
        if result["status"] is 'OK':
            woeid = result['address']
            latitude = result['lat']
            longitude = result['lng']
            location = result['address']
            units = 'si'
            timezone = get_timezone(bot, latitude, longitude)
        else:
            bot.write('API might be down, Blame bob')
        bot.db.set_nick_value(nick, 'woeid', woeid)
        bot.db.set_nick_value(nick, 'latitude', latitude)
        bot.db.set_nick_value(nick, 'longitude', longitude)
        bot.db.set_nick_value(nick, 'location', location)
        bot.db.set_nick_value(nick, 'tz', timezone)

        name = result['address']
        town = ''
        try:
            city = result['city']
        except:
            city = ''
        try:
            state = result['state']
        except:
            state = ''
        try:
            country = result['country']
        except:
            country = ''

        uid, station_name = aqicn_uid_search(bot, trigger.group(2))
        if uid:
            bot.db.set_nick_value(nick, 'uid', uid)
        else:
            uid = '?'
            station_name = '?'

        bot.reply('I now have you at WOEID %s (%s %s, %s, %s, %s.), timezone %s and at uid %s-%s' %
                  (woeid, name, town, city, state, country, timezone, uid, station_name))

    else:
        bot.reply("I can't remember that; I don't have a database.")

def weabase(bot, latitude, longitude, location, units='si'):
    forecast_url = 'https://api.forecast.io/forecast/' + bot.config.apikeys.darksky_key + '/' + str(latitude) + ',' + str(longitude) + '?units=' + units
    json_forecast = requests.get(forecast_url).json()
    nowwea = json_forecast['currently']
    today = json_forecast['daily']['data'][0]
    timezone = json_forecast['timezone']
    units = json_forecast['flags']['units']
    if units == 'us':
        deg = degf
        opp_deg = defc
        windspeedunits = "mph"
        opp_windspeedunits = "m/s"
    else:
        deg = degc
        opp_deg = degf
        windspeedunits = "m/s"
        opp_windspeedunits = "mph"
    return "{}: {}{} ({}{}) {}. Wind {} {} {} ({} {}). Humidity: {}. Feels like {} ({}) Sunrise: {} Sunset {}".format(location, str(int(nowwea["temperature"])), deg, str(c_to_f(int(nowwea["temperature"]))), opp_deg, nowwea["summary"], degreeToDirection(nowwea["windBearing"]), str(round(nowwea["windSpeed"],1)), windspeedunits, str(round(ms_to_mph(nowwea["windSpeed"]),1)), opp_windspeedunits, str(nowwea["humidity"]), str(round(nowwea["apparentTemperature"],1)), str(round(c_to_f(nowwea["apparentTemperature"]),1)), str(convert_unixtime_to_local(today['sunriseTime'], timezone)), str(convert_unixtime_to_local(today['sunsetTime'], timezone)) )

def wfbase(bot, latitude, longitude, location, units='si'):
    forecast_url = 'https://api.forecast.io/forecast/' + bot.config.apikeys.darksky_key + '/' + str(latitude) + ',' + str(longitude) + '?units=' + units
    weajson = requests.get(forecast_url).json()
    currentwea = weajson['daily']['data'][0]
    tomwea = weajson['daily']['data'][1]
    units = weajson['flags']['units']
    if units == 'us':
        deg = degf
    else:
        deg = degc
    return '{location} - Today: {min_temp} to {max_temp}{deg} {summary} Tomorrow: {tom_min} to {tom_max}{deg} {tom_summary} This Week: {week_summary}'.format(location=location, min_temp=str(int(round(currentwea["temperatureMin"]))), max_temp=str(int(round(currentwea["temperatureMax"]))), deg=deg, summary=currentwea["summary"],
                                                                                                                                                                                                        tom_min=str(int(round(tomwea["temperatureMin"]))), tom_max=str(int(round(tomwea["temperatureMax"]))), tom_summary=tomwea["summary"],
                                                                                                                                                                                                        week_summary=weajson['daily']['summary'])

def w5base(bot, latitude, longitude, location, units='si'):
    forecast_url = 'https://api.forecast.io/forecast/' + bot.config.apikeys.darksky_key + '/' + str(latitude) + ',' + str(longitude) + '?units=' + units
    weajson = requests.get(forecast_url).json()
    wea_forecast = weajson['daily']['data']
    units = weajson['flags']['units']
    if units == 'us':
        deg = degf
    else:
        deg = degc
    return """{location} - Tomorrow: {min_temp} to {max_temp}{deg} {summary}, 
{two_days}: {two_days_min} to {two_days_max}{deg} {two_days_summary}, 
{three_days}: {three_days_min} to {three_days_max}{deg} {three_days_summary}, 
{four_days}: {four_days_min} to {four_days_max}{deg} {four_days_summary}, 
{five_days}: {five_days_min} to {five_days_max}{deg} {five_days_summary}""" \
              .format(location=location, deg=deg, 
                      min_temp=str(int(round(wea_forecast[1]["temperatureMin"]))), 
                      max_temp=str(int(round(wea_forecast[1]["temperatureMax"]))), 
                      summary=wea_forecast[1]["summary"], 
                      two_days=timestamp_to_date(wea_forecast[2]['time']), 
                      two_days_min=str(int(round(wea_forecast[2]["temperatureMin"]))), 
                      two_days_max=str(int(round(wea_forecast[2]["temperatureMax"]))), 
                      two_days_summary=wea_forecast[2]["summary"], 
                      three_days=timestamp_to_date(wea_forecast[3]['time']), 
                      three_days_min=str(int(round(wea_forecast[3]["temperatureMin"]))), 
                      three_days_max=str(int(round(wea_forecast[3]["temperatureMax"]))),
                      three_days_summary=wea_forecast[3]["summary"],  
                      four_days=timestamp_to_date(wea_forecast[4]['time']),
                      four_days_min=str(int(round(wea_forecast[4]["temperatureMin"]))), 
                      four_days_max=str(int(round(wea_forecast[4]["temperatureMax"]))),
                      four_days_summary=wea_forecast[4]["summary"],  
                      five_days=timestamp_to_date(wea_forecast[5]['time']), 
                      five_days_min=str(int(round(wea_forecast[5]["temperatureMin"]))), 
                      five_days_max=str(int(round(wea_forecast[5]["temperatureMax"]))),
                      five_days_summary=wea_forecast[5]["summary"], 
                      )

def wcbase(bot, latitude, longitude, location, units='si'):
    forecast_url = 'https://api.forecast.io/forecast/' + bot.config.apikeys.darksky_key + '/' + str(latitude) + ',' + str(longitude) + '?units=' + units
    json_forecast = requests.get(forecast_url).json()

    nowwea = json_forecast['currently']
    currentwea = json_forecast['daily']['data'][0]
    tomwea = json_forecast['daily']['data'][1]
    timezone = get_timezone(bot, latitude, longitude)
    units = json_forecast['flags']['units']
    if units == 'us':
        deg = degf
        opp_deg = defc
        windspeedunits = "mph"
        opp_windspeedunits = "m/s"
    else:
        deg = degc
        opp_deg = degf
        windspeedunits = "m/s"
        opp_windspeedunits = "mph"
    wea_text = "{}: {}{} ({}{}) {}. Wind {} {} {} ({} {}). Humidity: {}. Feels like {} ({}) Sunrise: {} Sunset {}".format(location, str(int(nowwea["temperature"])), deg, str(c_to_f(int(nowwea["temperature"]))), opp_deg, nowwea["summary"], degreeToDirection(nowwea["windBearing"]), str(round(nowwea["windSpeed"],1)), windspeedunits, str(round(ms_to_mph(nowwea["windSpeed"]),1)), opp_windspeedunits, str(nowwea["humidity"]), str(round(nowwea["apparentTemperature"],1)), str(round(c_to_f(nowwea["apparentTemperature"]),1)), convert_unixtime_to_local(currentwea['sunriseTime'], timezone), convert_unixtime_to_local(currentwea['sunsetTime'], timezone) )

    wf_text = 'Today: {min_temp} to {max_temp}{deg} {summary} Tomorrow: {tom_min} to {tom_max}{deg} {tom_summary} This Week: {week_summary}'.format(location=location, min_temp=str(int(round(currentwea["temperatureMin"]))), max_temp=str(int(round(currentwea["temperatureMax"]))), deg=deg, summary=currentwea["summary"],
                                                                                                                                                                                                        tom_min=str(int(round(tomwea["temperatureMin"]))), tom_max=str(int(round(tomwea["temperatureMax"]))), tom_summary=tomwea["summary"],
                                                                                                                                                                                                        week_summary=json_forecast['daily']['summary'])
    return wea_text + " " + wf_text

def old_wea(woeid):
    query = web.urlencode({'w': woeid, 'u': 'c'})
    url = 'http://weather.yahooapis.com/forecastrss?' + query
    parsed = feedparser.parse(url)
    location = parsed['feed']['title']

    cover = get_cover(parsed)
    temp = get_temp(parsed)
    pressure = get_pressure(parsed)
    wind = get_wind(parsed)
    bot.say('%s: %s, %s, %s, %s' % (location, cover, temp, pressure, wind))

def c_to_f(temp):
    return round(temp * 1.8 + 32, 2)

def ms_to_mph(speed):
    return speed * 2.23694

def get_timezone(bot, lat, lon):
    """ Not used anymore. Yahoo API returns it all """
    timezonedb_url = "http://api.geonames.org/timezoneJSON?lat={}&lng={}&username={}".format(lat, lon, bot.config.apikeys.geonames_username)
    tz_json = requests.get(timezonedb_url).json()
    return tz_json['timezoneId']

@commands('weac', 'weaf')
def weather_deprecated_message(bot, trigger):
	bot.say("weac and weaf are deprecated. Please use .wea instead")
	weather(bot, trigger)
