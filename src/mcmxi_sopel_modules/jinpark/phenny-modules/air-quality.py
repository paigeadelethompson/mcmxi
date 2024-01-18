# -*- coding: utf8 -*-

from sopel import web
from sopel.module import commands, example

import requests
import datetime

BASE_URL = "http://api.waqi.info/"
SEARCH_URL = "http://api.waqi.info/search/?token={}&keyword={}"
FEED_URL = "http://api.waqi.info/feed/@{}/?token={}"
LAT_LNG_FEED_URL = "http://api.waqi.info/feed/geo:{};{}/?token={}"
GEOCODE_URL = "http://www.mapquestapi.com/geocoding/v1/address?key={}&location={}"
AIRVISUAL_LAT_LNG = "http://api.airvisual.com/v2/nearest_city?key={}&lat={}&lon={}"

def geocode(bot, location):
    key = bot.config.apikeys.mapquest_key
    search = requests.get(GEOCODE_URL.format(key, location)).json()
    status = search["info"]["statuscode"]
    if status == 0 and len(search["results"]) > 0 and len(search["results"][0]["locations"]) > 0:
        found_location = search["results"][0]["locations"][0]
        lat = search["results"][0]["locations"][0]["latLng"]["lat"]
        lng = search["results"][0]["locations"][0]["latLng"]["lng"]
        return lat, lng
    return None, None

def airvisual_lag_lng(bot, lat, lng):
    key = bot.config.apikeys.airvisual_key
    search = requests.get(AIRVISUAL_LAT_LNG.format(key, lat, lng)).json()
    if search["status"] == "success":
        aqi = search["data"]["current"]["pollution"]["aqius"]
        city = search["data"]["city"]
        state = search["data"]["state"]
        updated_time = search["data"]["current"]["pollution"]["ts"]
        return aqi, city, state, updated_time
    return None, None, None, None

def search_keyword(bot, location):
    key = bot.config.apikeys.aqicn_key
    search = requests.get(SEARCH_URL.format(key, location)).json()
    uid = search["data"][0]["station"]["uid"]
    feed = requests.get(FEED_URL.format(uid)).json()
    return feed["data"]

def get_feed(bot, uid):
    key = bot.config.apikeys.aqicn_key
    r = requests.get(FEED_URL.format(uid, key)).json()
    return r

def aqicn_uid_lat_lng_search(bot, lat, lng):
    key = bot.config.apikeys.aqicn_key
    search = requests.get(LAT_LNG_FEED_URL.format(lat, lng, key)).json()
    # if search["status"] == 'OK'
    uid = search["data"]["idx"]
    return uid

def search_keyword_uid(bot, location):
    key = bot.config.apikeys.aqicn_key
    search = requests.get(SEARCH_URL.format(key, location)).json()
    if len(search["data"]) == 0 or search["data"][0]["aqi"] != "-":
        return
    uid = search["data"][0]["uid"]
    return uid

def aqi_status(aqi):
    if aqi and isinstance( aqi, int ):
        if aqi < 50:
            return "Good"
        elif 50 <= aqi < 100:
            return "Moderate"
        elif 100 <= aqi < 150:
            return "Unhealthy for Sensitive Groups"
        elif 150 <= aqi < 200:
            return "Unhealthy"
        elif 250 <= aqi < 300:
            return "Very Unhealthy"
        elif aqi > 300:
            return "Hazardous"
    return 'Unknown'

#def construct_airq_string(bot, uid, second=False):
#    print('second time ', second, datetime.datetime.now())
#    data = get_feed(bot, uid)
#    if data["status"] == "ok":
#        data = data["data"]
#        aqi = data["aqi"]
#        city = data["city"]["name"]
#        try:
#            dominant_pollution = data["dominentpol"]
#        except:
#            dominant_pollution = '?'
#        try:
#            pm25 = data["iaqi"]["pm25"]["v"]
#        except:
#            pm25 = '?'
#        try:
#            pm10 = data["iaqi"]["pm10"]["v"]
#        except:
#            pm10 = '?'
#        status = aqi_status(aqi)
#        return "Current Air Quality in {} is {}. AQI is {}. Dominant pollution is {}. pm25: {} pm10: {}" \
#                .format(city, status, aqi, dominant_pollution, pm25, pm10)
#    if second == False:
#        construct_airq_string(bot, uid, True)
#    return "stupid bob"

def construct_latlng_airq_string(bot, lat, lng):
    aqi, city, state, update_time = airvisual_lag_lng(bot, lat, lng)
    if aqi:
        status = aqi_status(aqi)
        updated_datetime = datetime.datetime.strptime(update_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        return "Current Air Quality in {}, {} is {}. AQI is {}. Updated at {} UTC" \
                .format(city, state, status, aqi, updated_datetime.strftime("%m-%d %H:%M"))
    return "stupid bob. airv aqi failed for some reason"

def construct_short_airq_string(aqi, city, state):
    status = aqi_status(aqi)
    return "Current Air Quality in {}, {} is {}. AQI is {}." \
            .format(city, state, status, aqi)

@commands('air', 'aq', 'airq')
@example('.air seoul')
def air_quality_test(bot, trigger):
    """.air location - Show the air quality at the given location."""
    # If no input, check current user. If input, check if input is a user or search location instead
    airquality_text = ''
    location_or_nick = trigger.group(2)
    try:
        location_or_nick = trigger.group(2).lower()
        location_or_nick = location_or_nick.strip()
    except:
        location_or_nick = ''

    nick = trigger.nick.lower()

    if not location_or_nick:
        latitude = bot.db.get_nick_value(nick, 'latitude')
        longitude = bot.db.get_nick_value(nick, 'longitude')
        airquality_text = construct_latlng_airq_string(bot, latitude, longitude)
        if not latitude:
            return bot.msg(trigger.sender, "I don't know where you live. " +
                        'Give me a location, like .air London, or tell me where you live by saying .setlocation London, for example.')
    else:
        if bot.db.get_nick_value(nick, 'latitude'):
            nick = location_or_nick
            latitude = bot.db.get_nick_value(nick, 'latitude')
            longitude = bot.db.get_nick_value(nick, 'longitude')
            if latitude:
                airquality_text = construct_latlng_airq_string(bot, latitude, longitude)

    if not airquality_text:
        latitude, longitude = geocode(bot, location_or_nick)
        if latitude:
            airquality_text = construct_latlng_airq_string(bot, latitude, longitude)
        else:
            return bot.reply("I don't know where that is.")

    bot.say(airquality_text)
