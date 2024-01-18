"""
warnings.py -- NWS Alert Module
Copyright 2011, Michael Yanovich, yanovich.net

http://sopel.chat

This module allows one to query the National Weather Service for active
watches, warnings, and advisories that are present.
"""
from __future__ import print_function
from sopel.module import commands, priority
import feedparser
import re
import urllib
import sopel.web as web

states = {
    "alabama": "al",
    "alaska": "ak",
    "arizona": "az",
    "arkansas": "ar",
    "california": "ca",
    "colorado": "co",
    "connecticut": "ct",
    "delaware": "de",
    "florida": "fl",
    "georgia": "ga",
    "hawaii": "hi",
    "idaho": "id",
    "illinois": "il",
    "indiana": "in",
    "iowa": "ia",
    "kansas": "ks",
    "kentucky": "ky",
    "louisiana": "la",
    "maine": "me",
    "maryland": "md",
    "massachusetts": "ma",
    "michigan": "mi",
    "minnesota": "mn",
    "mississippi": "ms",
    "missouri": "mo",
    "montana": "mt",
    "nebraska": "ne",
    "nevada": "nv",
    "new hampshire": "nh",
    "new jersey": "nj",
    "new mexico": "nm",
    "new york": "ny",
    "north carolina": "nc",
    "north dakota": "nd",
    "ohio": "oh",
    "oklahoma": "ok",
    "oregon": "or",
    "pennsylvania": "pa",
    "rhode island": "ri",
    "south carolina": "sc",
    "south dakota": "sd",
    "tennessee": "tn",
    "texas": "tx",
    "utah": "ut",
    "vermont": "vt",
    "virginia": "va",
    "washington": "wa",
    "west virginia": "wv",
    "wisconsin": "wi",
    "wyoming": "wy",
}

county_list = "http://alerts.weather.gov/cap/{0}.php?x=3"
alerts = "http://alerts.weather.gov/cap/wwaatmget.php?x={0}"
zip_code_lookup = "http://www.zip-codes.com/zip-code/{0}/zip-code-{0}.asp"
nomsg = "There are no active watches, warnings or advisories, for {0}."
re_fips = re.compile(r'County FIPS:</a></td><td class="info">(\S+)</td></tr>')
re_state = re.compile(r'State:</a></td><td class="info"><a href="/state/\S\S.asp">\S\S \[(\S+(?: \S+)?)\]</a></td></tr>')
re_city = re.compile(r'City:</a></td><td class="info"><a href="/city/\S+.asp">(.*)</a></td></tr>')
more_info = "Complete weather watches, warnings, and advisories for {0}, available here: {1}"


@commands('nws')
@priority('high')
def nws_lookup(bot, trigger):
    """ Look up weather watches, warnings, and advisories. """
    text = trigger.group(2)
    if not text:
        return
    bits = text.split(",")
    master_url = False
    if len(bits) == 2:
        ## county given
        url_part1 = "http://alerts.weather.gov"
        state = bits[1].lstrip().rstrip().lower()
        county = bits[0].lstrip().rstrip().lower()
        if state not in states:
            bot.reply("State not found.")
            return
        url1 = county_list.format(states[state])
        page1 = web.get(url1).split("\n")
        for line in page1:
            mystr = ">" + unicode(county) + "<"
            if mystr in line.lower():
                url_part2 = line[9:36]
                break
        if not url_part2:
            bot.reply("Could not find county.")
            return
        master_url = url_part1 + url_part2
        location = text
    elif len(bits) == 1:
        ## zip code
        if bits[0]:
            urlz = zip_code_lookup.format(bits[0])
            pagez = web.get(urlz)
            fips = re_fips.findall(pagez)
            if fips:
                state = re_state.findall(pagez)
                city = re_city.findall(pagez)
                if not state and not city:
                    bot.reply("Could not match ZIP code to a state")
                    return
                state = state[0].lower()
                state = states[state].upper()
                location = city[0] + ", " + state
                fips_combo = unicode(state) + "C" + unicode(fips[0])
                master_url = alerts.format(fips_combo)
            else:
                bot.reply("ZIP code does not exist.")
                return

    if not master_url:
        bot.reply("Invalid input. Please enter a ZIP code or a county and state pairing, such as 'Franklin, Ohio'")
        return

    feed = feedparser.parse(master_url)
    warnings_dict = {}
    for item in feed.entries:
        if nomsg[:51] == item["title"]:
            bot.reply(nomsg.format(location))
            return
        else:
            warnings_dict[unicode(item["title"])] = unicode(item["summary"])

    paste_code = ""
    for alert in warnings_dict:
        paste_code += item["title"] + "\n" + item["summary"] + "\n\n"

    paste_dict = {
        "paste_private": 0,
        "paste_code": paste_code,
    }

    pastey = urllib.urlopen("http://pastebin.com/api_public.php",
        urllib.urlencode(paste_dict)).read()

    if len(warnings_dict) > 0:
        if trigger.sender.startswith('#'):
            i = 1
            for key in warnings_dict:
                if i > 1:
                    break
                bot.reply(key)
                bot.reply(warnings_dict[key][:510])
                i += 1
            bot.reply(more_info.format(location, master_url))
        else:
            for key in warnings_dict:
                bot.msg(trigger.nick, key)
                bot.msg(trigger.nick, warnings_dict[key])
            bot.msg(trigger.nick, more_info.format(location, master_url))

if __name__ == '__main__':
    print(__doc__.strip())
