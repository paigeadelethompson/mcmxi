"""
Sopel module for Jobs APIs.
Supports 3 public APIs with no authentication required.
"""

from sopel import plugin
import json
import sys
import os
# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get_module_logger, HTTPClient, IRCFormatter

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)
formatter = IRCFormatter()


# API definitions
APIS = [
    {
        'name': 'Arbeitnow',
        'description': 'API for Job board aggregator in Europe / Remote',
        'link': 'https://documenter.getpostman.com/view/18545278/UVJbJdKh',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'DevITjobs UK',
        'description': 'Jobs with GraphQL',
        'link': 'https://devitjobs.uk/job_feed.xml',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Jobicy',
        'description': 'Remote Jobs API Feed',
        'link': 'https://jobicy.com/jobs-rss-feed',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('jobs')
@plugin.command('jobs')
@plugin.example(f'.jobs')
def jobs_list(bot, trigger):
    """List all available Jobs APIs."""
    bot.say(f'Available Jobs APIs (3):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .jobs_info <name> for details')


@plugin.command('jobs_info')
@plugin.example(f'.jobs_info <name>')
def jobs_info(bot, trigger):
    """Get information about a specific Jobs API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .jobs_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.notice(trigger.nick, f'API not found: {trigger.group(2)}')


@plugin.command('jobs_search')
@plugin.example(f'.jobs_search <query>')
def jobs_search(bot, trigger):
    """Search Jobs APIs by name or description."""
    if not trigger.group(2):
        bot.notice(trigger.nick, f'Usage: .jobs_search <query>')
        return

    query = trigger.group(2).strip().lower()
    results = []
    for api in APIS:
        if (query in api['name'].lower() or query in api['description'].lower()):
            results.append(api)

    if not results:
        bot.notice(trigger.nick, f'No APIs found matching: {trigger.group(2)}')
        return

    bot.say(f'Found {len(results)} API(s):')
    for api in results[:5]:  # Show first 5 results
        bot.say(f"- {api['name']}: {api['description'][:60]}")
    if len(results) > 5:
        bot.say(f'... and {len(results) - 5} more results')


@plugin.command('job_arbeitnow')
@plugin.example('.job_arbeitnow python')
@plugin.example('.job_arbeitnow remote')
def job_arbeitnow(bot, trigger):
    """Search for jobs using Arbeitnow API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .job_arbeitnow <keyword>')
        bot.notice(trigger.nick, 'Example: .job_arbeitnow python')
        return
    
    keyword = trigger.group(2).strip()
    logger.info(f'Job search: {keyword}')
    
    encoded_keyword = http.quote(keyword)
    url = f'https://arbeitnow.com/api/job-board-api?search={encoded_keyword}&limit=3'
    
    logger.debug(f'Searching jobs: {url}')
    data = http.get(url)
    
    if not data or 'data' not in data:
        bot.notice(trigger.nick, f'No jobs found for "{keyword}" or API error.')
        return
    
    jobs = data.get('data', [])[:3]
    
    if not jobs:
        bot.notice(trigger.nick, f'No jobs found for "{keyword}"')
        return
    
    bot.say(f'Found {len(jobs)} job(s) for "{keyword}":')
    for job in jobs:
        title = job.get('title', 'Unknown')
        company = job.get('company_name', 'Unknown')
        location = job.get('location', 'Unknown')
        remote = job.get('remote', False)
        url_job = job.get('url', '')
        
        response = f"{formatter.bold(title)}"
        if company:
            response += f" @ {formatter.italic(company)}"
        if location:
            response += f" | {formatter.italic(location)}"
        if remote:
            response += f" | {formatter.bold('Remote')}"
        
        bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Jobs APIs loaded."""
    bot.memory['jobs_loaded'] = True
    bot.memory['jobs_count'] = 3
    logger.info('Jobs module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['jobs_loaded'] = False
    logger.info('Jobs module unloaded')
