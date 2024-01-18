# -*- coding: utf8 -*-
"""
visualcrossing.py - sopel weatherstack! Weather Module

"""

from sopel import web
from sopel.module import commands, example

from datetime import datetime
import feedparser
from lxml import etree
import requests
import pytz
import geocoder
import itertools

degc = "\xb0C"
degf = "\xb0F"
bold = "\x02"
forc = ['f','F','c','C']

AQI_SEARCH_URL = "http://api.waqi.info/search/?token={}&keyword={}"
WEATHERSTACK_SEARCH_URL="http://api.weatherstack.com/current?access_key={}&units={}&query={}"
VISUALCROSSING_URL="https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{}?key={}&unitGroup={}"

def degreeToDirection(deg):
  if not (isinstance(deg, float) or isinstance(deg, int)):
    return "?"
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


@commands('wc', 'wf', 'forecast', 'weather', 'wea')
@example('.wc London')
def weather_combined(bot, trigger):
    """.wc location - Show the weather and forecast at the given location."""

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
            result = geocoder_search(bot, location)
            if result and result["status"] is 'OK':
                woeid = result['address']
                latitude = result['lat']
                longitude = result['lng']
                location = result['address']

    if not woeid:
        return bot.reply("I don't know where that is.")

    wc_text = wcbase(bot, latitude, longitude, location)
    bot.say(wc_text)

@commands('w5', 'wd')
@example('.w5 London')
def weather_five_days(bot, trigger):
    """.w5 location - Show the weather forecast at the given location for the next 4 days."""

    location = trigger.group(2)
    try:
        location = trigger.group(2).lower()
    except:
        location = ''
    woeid = ''
    units = 'm'
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
            result = geocoder_search(bot, location)
            if result["status"] is 'OK':
                woeid = result['address']
                latitude = result['lat']
                longitude = result['lng']
                location = result['address']
                units = 'si'

    if not woeid:
        return bot.reply("I don't know where that is.")

    w5_text = w5base(bot, latitude, longitude, location)
    bot.say(w5_text)

@commands('setlocation', 'setloc')
@example('.setlocation Columbus, OH')
def update_woeid(bot, trigger):
    """Set your default weather location."""
    if bot.db:
        nick = trigger.nick.lower()
        location = trigger.group(2)
        result = geocoder_search(bot, location)
        if result["status"] is 'OK':
            woeid = result['address']
            latitude = result['lat']
            longitude = result['lng']
            location = result['address']
            units = 'm'
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

def w5base(bot, latitude, longitude, location):
    forecast_url = VISUALCROSSING_URL.format("{},{}".format(latitude, longitude), bot.config.apikeys.visualcrossing_key, 'metric')
    forecast_json = requests.get(forecast_url).json()
    five_day_forecast = forecast_json['days'][1:6]
    format_list = [
        (
            timestamp_to_date(d['datetimeEpoch']),
            d['tempmin'],
            d['tempmax'],
            d['description']
        ) for d in five_day_forecast
    ]
    format_list = list(itertools.chain(*format_list))
    format_list[0] = "Tomorrow"
    print(format_list)
    return """{location} - {0}: {1} to {2}{deg} {3}, 
{4}: {5} to {6}{deg} {7}, 
{8}: {9} to {10}{deg} {11}, 
{12}: {13} to {14}{deg} {15}, 
{16}: {17} to {18}{deg} {19}""" \
              .format(*format_list, location=location, deg=degc)

def wcbase(bot, latitude, longitude, location):
    forecast_url = VISUALCROSSING_URL.format("{},{}".format(latitude, longitude), bot.config.apikeys.visualcrossing_key, 'metric')
    json_forecast = requests.get(forecast_url)
    print(forecast_url)
    json_forecast = requests.get(forecast_url).json()

    current_weather = json_forecast['currentConditions']
    today_wea = json_forecast['days'][0]
    tom_wea = json_forecast['days'][1]

    main_temp_unit = degc
    second_temp_unit = degf
    main_wind_unit = "km/h"
    second_wind_unit = "mph"
    now_format_dict = {
        "location": location,
        "main_temp": current_weather['temp'],
        "main_temp_unit": main_temp_unit,
        "second_temp": str(c_to_f(float(current_weather['temp']))),
        "second_temp_unit": second_temp_unit,
        "current_description": current_weather['conditions'],
        "wind_direction": degreeToDirection(current_weather['winddir']),
        "main_wind_speed": current_weather['windspeed'] or  "?",
        "main_wind_unit": main_wind_unit,
        "second_wind_speed": kmph_to_mph(current_weather["windspeed"]),
        "second_wind_unit": second_wind_unit,
        "humidity": current_weather['humidity'],
        "main_feels_like": current_weather['feelslike'],
        "second_feels_like": str(round(c_to_f(current_weather['feelslike']),1)),
        "sunrise_time": current_weather['sunrise'],
        "sunset_time": current_weather['sunset']
    }
    two_day_format_dict = {
        "today_min": today_wea['tempmin'],
        "today_max": today_wea['tempmax'],
        "deg": main_temp_unit,
        "today_summary": today_wea['description'],
        "tom_min": tom_wea['tempmin'],
        "tom_max": tom_wea['tempmax'],
        "deg": main_temp_unit,
        "tom_summary": tom_wea['description'],
        "week_summary": json_forecast['description']
    }
    wea_text = """{location}: {main_temp}{main_temp_unit} ({second_temp}{second_temp_unit}) {current_description}. \
Wind {wind_direction} {main_wind_speed} {main_wind_unit} ({second_wind_speed} {second_wind_unit}). \
Humidity: {humidity}. Feels like {main_feels_like} ({second_feels_like}) Sunrise: {sunrise_time} Sunset {sunset_time}""".format(**now_format_dict)
                    
    wf_text = 'Today: {today_min} to {today_max}{deg} {today_summary} Tomorrow: {tom_min} to {tom_max}{deg} {tom_summary} This Week: {week_summary}'.format(**two_day_format_dict)        
    
    return wea_text + " " + wf_text

def c_to_f(temp):
    return round(temp * 1.8 + 32, 2)

def ms_to_mph(speed):
    if not (isinstance(speed, float) or isinstance(speed, int)):
        return "?"
    return str(round(speed * 2.23694, 1))

def kmph_to_mph(speed):
    if not (isinstance(speed, float) or isinstance(speed, int)):
        return "?"
    return str(round(speed * 0.621371, 1))

def get_timezone(bot, lat, lon):
    """ Not used anymore. Yahoo API returns it all """
    timezonedb_url = "http://api.geonames.org/timezoneJSON?lat={}&lng={}&username={}".format(lat, lon, bot.config.apikeys.geonames_username)
    tz_json = requests.get(timezonedb_url).json()
    return tz_json['timezoneId']

@commands('weac', 'weaf')
def weather_deprecated_message(bot, trigger):
	bot.say("weac and weaf are deprecated. Please use .wea instead")
	weather(bot, trigger)
