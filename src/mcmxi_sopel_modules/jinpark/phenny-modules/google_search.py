"""
google_search.py - Willie Google Search
"""

# from sopel.module import commands, example

# import requests
# import html.parser

# @commands('g', 'google')
# @example('.g San Francisco')
# def google_search(bot, trigger):
#     payload = {'q': trigger.group(2)}
#     json_response = requests.get('http://ajax.googleapis.com/ajax/services/search/web?v=1.0', params=payload).json()
#     results = json_response['responseData']['results']
#     if not results:
#     	bot.say('No results found.')
#     else:
#     	first_result = results[0]
#     	bot.say("{} - {}".format(first_result['unescapedUrl'], unescape_html(first_result['titleNoFormatting'])))

# def unescape_html(html_string):
#     return html.parser.HTMLParser().unescape(html_string)

# coding=utf-8
# Copyright 2008-9, Sean B. Palmer, inamidst.com
# Copyright 2012, Elsie Powell, embolalia.com
# Licensed under the Eiffel Forum License 2.
from __future__ import unicode_literals, absolute_import, print_function, division

import re
from sopel import web
from sopel.module import commands, example
import json
import sys
import requests
from bs4 import BeautifulSoup

if sys.version_info.major < 3:
    from urllib import quote_plus
else:
    from urllib.parse import quote_plus

def formatnumber(n):
    """Format a number with beautiful commas."""
    parts = list(str(n))
    for i in range((len(parts) - 3), 0, -3):
        parts.insert(i, ',')
    return ''.join(parts)

r_bing = re.compile(r'<h3><a href="([^"]+)"')


def bing_search(query, lang='en-US'):
    base = 'http://www.bing.com/search?mkt=%s&q=' % lang
    bytes = web.get(base + query)
    m = r_bing.search(bytes)
    if m:
        return m.group(1)

r_duck = re.compile(r'nofollow" class="[^"]+" href="(?!https?:\/\/r\.search\.yahoo)(.*?)">')


def duck_search(query):
    query = query.replace('!', '')
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
    uri = 'http://duckduckgo.com/html/?q=%s&kl=us-en' % query
    soup = BeautifulSoup(requests.get(uri, headers={'User-Agent': user_agent}).content, "html.parser")
    # if 'web-result' in bytes:  # filter out the adds on top of the page
    #     bytes = bytes.split('web-result')[2]
    # m = r_duck.search(bytes)
    # if m:
    #     return web.decode(m.group(1))
    if soup.select('.result__a'):
        return soup.select('.result__a')[2]['href']

# Alias google_search to duck_search
google_search = duck_search


def duck_api(query):
    if '!bang' in query.lower():
        return 'https://duckduckgo.com/bang.html'

    # This fixes issue #885 (https://github.com/sopel-irc/sopel/issues/885)
    # It seems that duckduckgo api redirects to its Instant answer API html page
    # if the query constains special charactares that aren't urlencoded.
    # So in order to always get a JSON response back the query is urlencoded
    query = quote_plus(query)
    uri = 'http://api.duckduckgo.com/?q=%s&format=json&no_html=1&no_redirect=1' % query
    results = json.loads(web.get(uri))
    if results['Redirect']:
        return results['Redirect']
    else:
        return None


@commands('duck', 'ddg')
@example('.duck privacy or .duck !mcwiki obsidian')
def duck(bot, trigger):
    """Queries Duck Duck Go for the specified input."""
    query = trigger.group(2)
    if not query:
        return bot.reply('.ddg what?')

    # If the API gives us something, say it and stop
    result = duck_api(query)
    if result:
        bot.reply(result)
        return

    # Otherwise, look it up on the HTMl version
    uri = duck_search(query)

    if uri:
        bot.reply(uri)
        if 'last_seen_url' in bot.memory:
            bot.memory['last_seen_url'][trigger.sender] = uri
    else:
        bot.reply("No results found for '%s'." % query)


@commands('searchb')
@example('.searchb nerdfighter')
def search(bot, trigger):
    """Searches Bing and Duck Duck Go."""
    if not trigger.group(2):
        return bot.reply('.search for what?')
    query = trigger.group(2)
    bu = bing_search(query) or '-'
    du = duck_search(query) or '-'

    if bu == du:
        result = '%s (b, d)' % bu
    else:
        if len(bu) > 150:
            bu = '(extremely long link)'
        if len(du) > 150:
            du = '(extremely long link)'
        result = '%s (b), %s (d)' % (bu, du)

    bot.reply(result)


@commands('suggest')
def suggest(bot, trigger):
    """Suggest terms starting with given input"""
    if not trigger.group(2):
        return bot.reply("No query term.")
    query = trigger.group(2)
    uri = 'http://websitedev.de/temp-bin/suggest.pl?q='
    answer = web.get(uri + query.replace('+', '%2B'))
    if answer:
        bot.say(answer)
    else:
        bot.reply('Sorry, no result.')

@commands('g', 'search')
def google_search(bot, trigger):
    query = quote_plus(trigger.group(2))
    GOOGLE_API_KEY = bot.config.apikeys.google
    GOOGLE_SEARCH_ENGINE_KEY = bot.config.apikeys.google_search
    r = requests.get(u"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_key}&q={query}".format(
        api_key=GOOGLE_API_KEY,
        search_engine_key=GOOGLE_SEARCH_ENGINE_KEY,
        query=query
    ))
    results = r.json()
    if results["searchInformation"]["totalResults"] != "0":
        first_result = results["items"][0]
        bot.say(u"{link} - {title}".format(link=first_result["link"], title=first_result["title"]))
        return
    else:
        bot.say("Sorry, no result. Blame bob.")
