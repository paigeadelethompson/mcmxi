# -*- coding: utf8 -*-
"""
jargon.py - Willie Jargon File Glossary Module
"""

from sopel.module import commands, example
from pymongo import MongoClient


def setup(bot):
    connection = MongoClient('ds041380.mongolab.com', 41380)
    db = connection['jargon_file']
    db.authenticate(bot.config.apikeys.mongo_username, bot.config.apikeys.mongo_password)
    bot.memory['mongodb'] = db

@commands('jargon', 'j')
@example('.j tm')
def jargon_search(bot, trigger):
    """.jargon search_term - finds definition and info about search_term from the jargon file glossary"""
    search_input = trigger.group(2)
    if not search_input:
        bot.say('You must enter a search term')
    else:
        db = bot.memory['mongodb']
        db_results = db.command('text', 'glossary', search=search_input, limit=1)
        if db_results['results']:
            result = db_results['results'][0]['obj']
            result_string = jargon_parse(result)
            bot.say(result_string)
        else:
            bot.say('No results found. Blame bob!')

def jargon_parse(jargon_dict):
    definitions = jargon_dict['definitions']
    parsed_definition = ""
    parsed_definition += '{}'.format(jargon_dict['word'])
    parsed_definition += ': '
    if jargon_dict['pronunciations']:
        for pronunciation in jargon_dict['pronunciations']:
            parsed_definition += pronunciation
            parsed_definition += ', '
    if jargon_dict['grammmar']:
        parsed_definition += jargon_dict['grammmar']
        parsed_definition += ' - '
    for definition in definitions:
        parsed_definition += '{}'.format(definition)
        parsed_definition += ' '
    return parsed_definition
