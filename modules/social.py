"""
Sopel module for Social APIs.
Supports 6 public APIs with no authentication required.
"""

import json
import os
import re
import sys
from html import unescape

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, IRCFormatter, get_module_logger, register_apis

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)
formatter = IRCFormatter()


# API definitions
APIS = [
    {
        'name': '4chan',
        'description': 'Simple image-based bulletin board dedicated to a variety of topics',
        'link': 'https://github.com/4chan/4chan-API',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'HackerNews',
        'description': 'Social news for CS and entrepreneurship',
        'link': 'https://github.com/HackerNews/API',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Hashnode',
        'description': 'A blogging platform built for developers',
        'link': 'https://hashnode.com',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Instagram Posts Generator',
        'description': 'Generate posts with templates from popular instagram pages.',
        'link': 'https://instagram-posts-generator.vercel.app/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Lanyard',
        'description': 'Retrieve your presence on Discord through an HTTP REST API or WebSocket',
        'link': 'https://github.com/Phineas/lanyard',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Open Collective',
        'description': 'Get Open Collective data',
        'link': 'https://docs.opencollective.com/help/developers/api',
        'https': True,
        'cors': 'unknown',
    },
]




@plugin.command('hn_hackernews')
@plugin.example('.hn_hackernews')
@plugin.example('.hn_hackernews 5')
def hn_hackernews(bot, trigger):
    """Get top HackerNews stories using HackerNews API."""
    limit = 3
    if trigger.group(2):
        try:
            limit = min(int(trigger.group(2).strip()), 5)  # Max 5 stories
        except ValueError:
            pass

    logger.info(f'Fetching HackerNews top stories (limit: {limit})')

    # Get top story IDs
    top_url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    logger.debug(f'Fetching top story IDs: {top_url}')
    top_ids = http.get(top_url)

    if not top_ids or not isinstance(top_ids, list):
        bot.notice(trigger.nick, 'Failed to fetch HackerNews stories. Please try again.')
        return

    # Get details for top N stories
    story_ids = top_ids[:limit]
    stories = []

    for story_id in story_ids:
        story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
        story_data = http.get(story_url)
        if story_data:
            stories.append(story_data)

    if not stories:
        bot.notice(trigger.nick, 'No stories found.')
        return

    bot.say(f'Top {len(stories)} HackerNews story(ies):')
    for i, story in enumerate(stories, 1):
        title = story.get('title', 'Unknown')
        score = story.get('score', 0)
        url = story.get('url', '')
        by = story.get('by', 'Unknown')

        response = f"{i}. {formatter.bold(title)}"
        response += f" | Score: {formatter.bold(str(score))} | by {formatter.italic(by)}"
        if url:
            # Extract domain from URL
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc.replace('www.', '')
                response += f" | {formatter.monospace(domain)}"
            except:
                pass

        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('chan_4chan')
@plugin.example('.chan_4chan b')
@plugin.example('.chan_4chan b 1')
def chan_4chan(bot, trigger):
    """Get 4chan threads using 4chan API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .chan_4chan <board> [page]')
        bot.notice(trigger.nick, 'Example: .chan_4chan b')
        bot.notice(trigger.nick, 'Example: .chan_4chan b 1')
        return

    parts = trigger.group(2).strip().split()
    board = parts[0].strip().lower()
    page = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1

    logger.info(f'Fetching 4chan board: /{board}/ page {page}')

    # Get threads from board page
    url = f'https://a.4cdn.org/{board}/{page}.json'

    logger.debug(f'Fetching 4chan threads: {url}')
    data = http.get(url)

    if not data or 'threads' not in data:
        bot.notice(trigger.nick, f'Failed to fetch 4chan board /{board}/ or invalid page.')
        return

    threads = data.get('threads', [])
    if not threads:
        bot.notice(trigger.nick, f'No threads found on /{board}/ page {page}.')
        return

    # Get top 3 threads
    top_threads = threads[:3]
    bot.say(f'Top 3 threads on /{board}/ page {page}:')

    for i, thread_data in enumerate(top_threads, 1):
        posts = thread_data.get('posts', [])
        if not posts:
            continue

        op = posts[0]  # First post is OP
        no = op.get('no', '')
        sub = op.get('sub', '')
        com = op.get('com', '')
        replies = op.get('replies', 0)
        images = op.get('images', 0)

        # Clean HTML from comment
        if com:
            # Remove HTML tags and decode entities
            com = re.sub(r'<[^>]+>', '', com)
            com = unescape(com)
            com = com.replace('\n', ' ').strip()[:100]

        response = f"{i}. /{board}/#{no}"
        if sub:
            response += f" | {formatter.bold(sub)}"
        if com:
            response += f" | {com}..."
        response += f" | {replies} replies, {images} images"

        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('chan_boards')
@plugin.example('.chan_boards')
def chan_boards(bot, trigger):
    """List available 4chan boards."""
    logger.info('Fetching 4chan boards list')

    url = 'https://a.4cdn.org/boards.json'

    logger.debug(f'Fetching 4chan boards: {url}')
    data = http.get(url)

    if not data or 'boards' not in data:
        bot.notice(trigger.nick, 'Failed to fetch 4chan boards list.')
        return

    boards = data.get('boards', [])
    if not boards:
        bot.notice(trigger.nick, 'No boards found.')
        return

    bot.say(f'4chan boards (showing first 10 of {len(boards)}):')
    for board in boards[:10]:
        board_code = board.get('board', '')
        title = board.get('title', 'Unknown')
        bot.say(f"/{board_code}/ - {formatter.bold(title)}")


@plugin.command('oc_opencollective')
@plugin.example('.oc_opencollective webpack')
def oc_opencollective(bot, trigger):
    """Get Open Collective account information using Open Collective API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .oc_opencollective <slug>')
        bot.notice(trigger.nick, 'Example: .oc_opencollective webpack')
        return

    slug = trigger.group(2).strip()

    logger.info(f'Fetching Open Collective account: {slug}')

    query = """
    query GetAccount($slug: String!) {
        account(slug: $slug) {
            name
            description
            slug
            website
            type
            stats {
                totalAmountRaised
                totalAmountSpent
                totalContributors
            }
        }
    }
    """

    variables = {'slug': slug}

    logger.debug(f'Executing GraphQL query for Open Collective: {slug}')

    # Execute GraphQL query directly using HTTP POST
    endpoint = 'https://api.opencollective.com/graphql/v2'
    payload = {'query': query, 'variables': variables}
    headers = {'Content-Type': 'application/json'}
    post_data = json.dumps(payload).encode('utf-8')
    result = http.post(endpoint, data=post_data, headers=headers)

    if not result or 'data' not in result or not result.get('data', {}).get('account'):
        bot.notice(trigger.nick, f'Open Collective account "{slug}" not found or API error.')
        return

    account = result['data']['account']
    name = account.get('name', 'Unknown')
    description = account.get('description', '')
    account_type = account.get('type', '')
    website = account.get('website', '')
    stats = account.get('stats', {})

    response = f"{formatter.bold(name)}"
    if account_type:
        response += f" ({account_type})"
    if description:
        desc = description[:100] if len(description) > 100 else description
        response += f" | {desc}"
    if website:
        response += f" | {formatter.monospace(website)}"

    bot.say(formatter.truncate(response, max_len=400))

    # Show stats if available
    if stats:
        raised = stats.get('totalAmountRaised', 0)
        spent = stats.get('totalAmountSpent', 0)
        contributors = stats.get('totalContributors', 0)

        stats_line = f"Raised: ${raised/100:.2f} | Spent: ${spent/100:.2f} | Contributors: {contributors}"
        bot.say(formatter.truncate(stats_line, max_len=400))


def setup(bot):
    """Module setup - Social APIs loaded."""
    register_apis('social', APIS)
    bot.memory['social_loaded'] = True
    bot.memory['social_count'] = 6
    logger.info('Social module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['social_loaded'] = False
    logger.info('Social module unloaded')
