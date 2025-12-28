"""
Sopel module for News APIs.
Supports 4 public APIs with no authentication required.
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
        'name': 'Chronicling America',
        'description': 'Provides access to millions of pages of historic US newspapers from the Library of Congress',
        'link': 'http://chroniclingamerica.loc.gov/about/api/',
        'https': False,
        'cors': 'unknown',
    },
    {
        'name': 'Inshorts News',
        'description': 'Provides news from inshorts',
        'link': 'https://github.com/cyberboysumanjay/Inshorts-News-API',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Spaceflight News',
        'description': 'Spaceflight related news 🚀',
        'link': 'https://spaceflightnewsapi.net',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Substack API Wrapper',
        'description': "Substack\'s newsletter platform now has an API wrapper, for easy access to latest posts",
        'link': 'https://github.com/NHagar/substack_api',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('news')
@plugin.command('news')
@plugin.example(f'.news')
def news_list(bot, trigger):
    """List all available News APIs."""
    bot.say(f'Available News APIs (4):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .news_info <name> for details')


@plugin.command('news_info')
@plugin.example(f'.news_info <name>')
def news_info(bot, trigger):
    """Get information about a specific News API."""
    if not trigger.group(2):
        bot.say(f'Usage: .news_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('news_search')
@plugin.example(f'.news_search <query>')
def news_search(bot, trigger):
    """Search News APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .news_search <query>')
        return

    query = trigger.group(2).strip().lower()
    results = []
    for api in APIS:
        if (query in api['name'].lower() or query in api['description'].lower()):
            results.append(api)

    if not results:
        bot.say(f'No APIs found matching: {trigger.group(2)}')
        return

    bot.say(f'Found {len(results)} API(s):')
    for api in results[:5]:  # Show first 5 results
        bot.say(f"- {api['name']}: {api['description'][:60]}")
    if len(results) > 5:
        bot.say(f'... and {len(results) - 5} more results')


@plugin.command('news_spaceflight')
@plugin.example('.news_spaceflight')
@plugin.example('.news_spaceflight 5')
def news_spaceflight(bot, trigger):
    """Get spaceflight news using Spaceflight News API."""
    limit = 3
    if trigger.group(2):
        try:
            limit = min(int(trigger.group(2).strip()), 5)  # Max 5 articles
        except ValueError:
            pass
    
    logger.info(f'Fetching spaceflight news (limit: {limit})')
    
    url = f'https://api.spaceflightnewsapi.net/v4/articles/?limit={limit}'
    
    logger.debug(f'Fetching spaceflight news: {url}')
    data = http.get(url)
    
    if not data or 'results' not in data:
        bot.notice(trigger.nick, 'Failed to fetch spaceflight news. Please try again.')
        return
    
    results = data.get('results', [])[:limit]
    
    if not results:
        bot.notice(trigger.nick, 'No spaceflight news found.')
        return
    
    bot.say(f'Latest spaceflight news ({len(results)} articles):')
    for article in results:
        title = article.get('title', 'Unknown')
        news_site = article.get('news_site', 'Unknown')
        published = article.get('published_at', '')[:10] if article.get('published_at') else 'Unknown'
        url_article = article.get('url', '')
        
        response = f"{formatter.bold(title)} | {formatter.italic(news_site)} | {formatter.monospace(published)}"
        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('news_inshorts')
@plugin.example('.news_inshorts')
@plugin.example('.news_inshorts technology')
@plugin.example('.news_inshorts sports')
def news_inshorts(bot, trigger):
    """Get news from Inshorts API."""
    # Inshorts News: https://github.com/cyberboysumanjay/Inshorts-News-API
    # Endpoint: https://inshortsapi.vercel.app/news?category={category}
    # Categories: all, national, business, sports, world, politics, technology, startup, entertainment, miscellaneous, science, automobile
    
    category = trigger.group(2).strip().lower() if trigger.group(2) else 'all'
    
    valid_categories = ['all', 'national', 'business', 'sports', 'world', 'politics', 
                       'technology', 'startup', 'entertainment', 'miscellaneous', 
                       'science', 'automobile']
    
    if category not in valid_categories:
        bot.notice(trigger.nick, f'Invalid category. Valid: {", ".join(valid_categories)}')
        return
    
    logger.info(f'Fetching Inshorts news: {category}')
    
    url = f'https://inshortsapi.vercel.app/news?category={http.quote(category)}'
    
    logger.debug(f'Fetching Inshorts news: {url}')
    data = http.get(url)
    
    if not data or 'data' not in data:
        bot.notice(trigger.nick, 'Failed to fetch Inshorts news. Please try again.')
        return
    
    articles = data.get('data', [])[:3]
    
    if not articles:
        bot.notice(trigger.nick, f'No news found for category "{category}".')
        return
    
    bot.say(f'Inshorts News ({formatter.bold(category)}) - {len(articles)} articles:')
    for article in articles:
        title = article.get('title', 'Unknown')
        content = article.get('content', '')
        author = article.get('author', 'Unknown')
        date = article.get('date', 'Unknown')
        read_more_url = article.get('readMoreUrl', '')
        
        response = f"{formatter.bold(title)}"
        if author and author != 'Unknown':
            response += f" | {formatter.italic(author)}"
        if date:
            response += f" | {formatter.monospace(date[:10])}"
        bot.say(formatter.truncate(response, max_len=400))
        
        if content:
            content_short = content[:150] + '...' if len(content) > 150 else content
            bot.say(f"  {formatter.italic(content_short)}")


@plugin.command('news_chronicling')
@plugin.example('.news_chronicling bitcoin')
@plugin.example('.news_chronicling "world war"')
def news_chronicling(bot, trigger):
    """Search historic US newspapers using Chronicling America API."""
    # Chronicling America: http://chroniclingamerica.loc.gov/about/api/
    # Endpoint: http://chroniclingamerica.loc.gov/search/pages/results/?format=json&q={query}&rows={limit}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .news_chronicling <search_query>')
        bot.notice(trigger.nick, 'Example: .news_chronicling bitcoin')
        bot.notice(trigger.nick, 'Example: .news_chronicling "world war"')
        return
    
    query = trigger.group(2).strip()
    logger.info(f'Chronicling America search: {query}')
    
    encoded_query = http.quote(query)
    url = f'http://chroniclingamerica.loc.gov/search/pages/results/?format=json&q={encoded_query}&rows=3'
    
    logger.debug(f'Searching Chronicling America: {url}')
    data = http.get(url)
    
    if not data or 'items' not in data:
        bot.notice(trigger.nick, f'No historic newspaper articles found for "{query}" or API error.')
        return
    
    items = data.get('items', [])[:3]
    
    if not items:
        bot.notice(trigger.nick, f'No historic newspaper articles found for "{query}".')
        return
    
    total_items = data.get('totalItems', len(items))
    bot.say(f'Historic Newspapers - Found {total_items:,} article(s) for "{query}" (showing {len(items)}):')
    
    for item in items:
        title = item.get('title', 'Unknown')
        date = item.get('date', 'Unknown')
        newspaper = item.get('title_normal', '')
        state = item.get('state', [])
        state_str = ', '.join(state[:2]) if state else 'Unknown'
        url_item = item.get('url', '')
        
        response = f"{formatter.bold(title)}"
        if date:
            response += f" | {formatter.monospace(date[:10])}"
        if state_str:
            response += f" | {formatter.italic(state_str)}"
        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('news_substack')
@plugin.example('.news_substack')
@plugin.example('.news_substack platformer')
def news_substack(bot, trigger):
    """Get latest posts from Substack newsletters using Substack API Wrapper."""
    # Substack API Wrapper: https://github.com/NHagar/substack_api
    # Note: This is a wrapper, endpoint may vary. Using common pattern.
    
    publication = trigger.group(2).strip().lower() if trigger.group(2) else ''
    
    if not publication:
        bot.notice(trigger.nick, 'Usage: .news_substack <publication_name>')
        bot.notice(trigger.nick, 'Example: .news_substack platformer')
        bot.notice(trigger.nick, 'Note: Publication name is the Substack publication slug')
        return
    
    logger.info(f'Substack lookup: {publication}')
    
    # Try common Substack API wrapper endpoints
    # The actual endpoint may vary based on the wrapper implementation
    url = f'https://substackapi.com/api/publication/{http.quote(publication)}/posts'
    
    logger.debug(f'Fetching Substack posts: {url}')
    data = http.get(url)
    
    if not data:
        # Try alternative endpoint pattern
        url_alt = f'https://api.substack.com/v1/publications/{http.quote(publication)}/posts'
        logger.debug(f'Trying alternative endpoint: {url_alt}')
        data = http.get(url_alt)
    
    if not data:
        bot.notice(trigger.nick, f'Failed to fetch Substack posts for "{publication}".')
        bot.notice(trigger.nick, 'The publication may not exist or the API endpoint may have changed.')
        return
    
    # Handle different response formats
    posts = []
    if isinstance(data, list):
        posts = data[:3]
    elif isinstance(data, dict):
        if 'posts' in data:
            posts = data['posts'][:3]
        elif 'data' in data:
            posts = data['data'][:3]
        elif 'results' in data:
            posts = data['results'][:3]
    
    if not posts:
        bot.notice(trigger.nick, f'No posts found for Substack publication "{publication}".')
        return
    
    bot.say(f'Substack - {formatter.bold(publication)} ({len(posts)} posts):')
    for post in posts:
        title = post.get('title', post.get('post_title', 'Unknown'))
        subtitle = post.get('subtitle', post.get('post_subtitle', ''))
        author = post.get('author', post.get('author_name', 'Unknown'))
        published = post.get('published_at', post.get('post_date', ''))
        url_post = post.get('canonical_url', post.get('url', ''))
        
        response = f"{formatter.bold(title)}"
        if author and author != 'Unknown':
            response += f" | {formatter.italic(author)}"
        if published:
            date_short = published[:10] if len(published) >= 10 else published
            response += f" | {formatter.monospace(date_short)}"
        bot.say(formatter.truncate(response, max_len=400))
        
        if subtitle:
            subtitle_short = subtitle[:100] + '...' if len(subtitle) > 100 else subtitle
            bot.say(f"  {formatter.italic(subtitle_short)}")


def setup(bot):
    """Module setup - News APIs loaded."""
    bot.memory['news_loaded'] = True
    bot.memory['news_count'] = 4
    logger.info('News module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['news_loaded'] = False
    logger.info('News module unloaded')
