"""
Sopel module for URL previews.
Supports OpenGraph, YouTube, GitHub, GitLab, LinkedIn, Twitter/X, Nitter, Nostr, Imgur, and Reddit.
"""

import os
import re
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, IRCFormatter, OpenGraphExtractor, get_module_logger

logger = get_module_logger(__name__)
http = HTTPClient(max_size=2 * 1024 * 1024)  # 2MB for previews
formatter = IRCFormatter()


# URL whitelist - stored in bot memory
# Format: [{'pattern': 'regex', 'enable_fields': ['og:field1', ...], 'disable_fields': ['og:field2', ...]}, ...]
def get_whitelist(bot):
    """Get URL whitelist entries from bot memory."""
    if 'preview_whitelist' not in bot.memory:
        bot.memory['preview_whitelist'] = []
    return bot.memory['preview_whitelist']


def is_url_whitelisted(bot, url: str) -> Optional[Dict[str, Any]]:
    """
    Check if URL matches any whitelist pattern.
    Returns the matching whitelist entry (with pattern, enable_fields, disable_fields) or None.
    """
    whitelist = get_whitelist(bot)
    try:
        for entry in whitelist:
            pattern = entry.get('pattern', '')
            if pattern and re.search(pattern, url, re.IGNORECASE):
                return entry
    except Exception as e:
        logger.exception('Error checking URL whitelist', e)
    return None


@plugin.url(r'https?://[^\s]+')
def preview_opengraph_handler(bot, trigger):
    """Preview URL using OpenGraph metadata (only for whitelisted URLs)."""
    url = trigger.group(0).strip()

    # Only preview if whitelisted
    whitelist_entry = is_url_whitelisted(bot, url)
    if not whitelist_entry:
        return

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')
    except Exception as e:
        logger.debug(f'Error parsing URL {url}: {e}')
        return

    # Skip URLs handled by specific handlers (non-OpenGraph)
    specific_handler_domains = [
        'youtube.com', 'youtu.be', 'youtube-nocookie.com', 'm.youtube.com',
        'github.com',
        'gitlab.com',
        'imgur.com', 'i.imgur.com',
        'reddit.com', 'old.reddit.com', 'np.reddit.com',
    ]
    
    if domain in specific_handler_domains:
        return

    enable_fields = whitelist_entry.get('enable_fields', [])
    disable_fields = whitelist_entry.get('disable_fields', [])
    preview_opengraph(bot, trigger, url, domain, enable_fields=enable_fields, disable_fields=disable_fields)


def preview_opengraph(bot, trigger, url: str, domain: str, enable_fields: Optional[List[str]] = None, disable_fields: Optional[List[str]] = None):
    """Preview URL using OpenGraph metadata with field filtering."""
    logger.info(f'Extracting OpenGraph data from: {url}')

    og_data = OpenGraphExtractor.extract_from_url(url, http_client=http)

    if not og_data:
        return

    enable_fields = enable_fields or []
    disable_fields = disable_fields or []

    # Filter fields based on enable/disable lists
    def should_show_field(field_name: str) -> bool:
        """Check if a field should be shown based on enable/disable lists.

        field_name can be like 'og:title', 'article:author', 'og:article:author', etc.
        enable_fields/disable_fields entries can be like 'og:title', 'article:author', etc.
        """
        # Normalize field name - check both with and without og: prefix
        field_variants = [field_name]
        if field_name.startswith('og:'):
            field_variants.append(field_name[3:])  # Remove og: prefix
        else:
            field_variants.append(f'og:{field_name}')  # Add og: prefix

        # If enable_fields is specified, only show those fields
        if enable_fields:
            for variant in field_variants:
                if variant in enable_fields or any(variant.startswith(ef) for ef in enable_fields):
                    return True
            return False

        # If disable_fields is specified, exclude those fields
        if disable_fields:
            for variant in field_variants:
                if variant in disable_fields or any(variant.startswith(df) for df in disable_fields):
                    return False

        # Default: show all fields
        return True

    # Filter og_data based on enable/disable lists
    filtered_data = {}
    for key, value in og_data.items():
        if should_show_field(key):
            filtered_data[key] = value

    # Use filtered data (or original if no filtering)
    if enable_fields or disable_fields:
        og_data = filtered_data

    # Always show title (required field)
    title = og_data.get('title', og_data.get('og:title', '')).strip()
    if not title:
        return

    # Build response with title and site name
    site_name = og_data.get('site_name', og_data.get('og:site_name', '')).strip()
    response_parts = [formatter.bold(title)]

    if site_name and site_name.lower() != domain:
        response_parts.append(f"| {formatter.italic(site_name)}")

    # Add type if available
    og_type = og_data.get('type', og_data.get('og:type', '')).strip()
    if og_type and should_show_field('og:type'):
        response_parts.append(f"| {formatter.monospace(og_type)}")

    bot.say(formatter.truncate(' '.join(response_parts), max_len=400))

    # Add description if available
    description = og_data.get('description', og_data.get('og:description', '')).strip()
    if description and should_show_field('og:description'):
        desc = description[:200] if len(description) > 200 else description
        bot.say(formatter.truncate(desc, max_len=400))

    # Add locale if available
    locale = og_data.get('og:locale', '').strip()
    if locale and should_show_field('og:locale'):
        bot.say(formatter.truncate(f"Locale: {formatter.monospace(locale)}", max_len=400))

    # Add article-specific fields
    if og_type in ['article', 'news'] or 'og:type' in og_data:
        article_fields = []
        author = og_data.get('article:author', og_data.get('og:article:author', '')).strip()
        if author and should_show_field('article:author'):
            article_fields.append(f"by {formatter.italic(author)}")

        pub_time = og_data.get('article:published_time', og_data.get('og:article:published_time', '')).strip()
        if pub_time and should_show_field('article:published_time'):
            article_fields.append(f"published: {formatter.monospace(pub_time[:10])}")

        section = og_data.get('article:section', og_data.get('og:article:section', '')).strip()
        if section and should_show_field('article:section'):
            article_fields.append(f"section: {formatter.monospace(section)}")

        tags = []
        if should_show_field('article:tag'):
            # Collect article tags (can be stored as 'og:article:tag')
            tag_value = og_data.get('og:article:tag', og_data.get('article:tag', ''))
            if tag_value:
                if isinstance(tag_value, list):
                    tags.extend(tag_value)
                else:
                    tags.append(tag_value)

        if tags:
            article_fields.append(f"tags: {', '.join(tags[:5])}")

        if article_fields:
            bot.say(formatter.truncate(' | '.join(article_fields), max_len=400))

    # Add image URL if available
    image = og_data.get('image', og_data.get('og:image', '')).strip()
    if image and should_show_field('og:image'):
        bot.say(formatter.truncate(f"Image: {formatter.monospace(image)}", max_len=400))

    # Add video URL if available
    video = og_data.get('og:video', '').strip()
    if not video and 'videos' in og_data:
        video = og_data['videos'][0] if og_data['videos'] else ''
    if video and should_show_field('og:video'):
        bot.say(formatter.truncate(f"Video: {formatter.monospace(video)}", max_len=400))

    # Add audio URL if available
    audio = og_data.get('og:audio', '').strip()
    if not audio and 'audios' in og_data:
        audio = og_data['audios'][0] if og_data['audios'] else ''
    if audio and should_show_field('og:audio'):
        bot.say(formatter.truncate(f"Audio: {formatter.monospace(audio)}", max_len=400))


@plugin.url(r'https?://(?:www\.)?(?:youtube\.com|youtu\.be|youtube-nocookie\.com|m\.youtube\.com)/.*')
def preview_youtube(bot, trigger):
    """Preview YouTube video (regular, movies, music)."""
    url = trigger.group(0).strip()

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')
    except Exception as e:
        logger.debug(f'Error parsing URL {url}: {e}')
        return

    preview_youtube_impl(bot, trigger, url, domain)


def preview_youtube_impl(bot, trigger, url: str, domain: str):
    """Preview YouTube video (regular, movies, music)."""
    logger.info(f'Extracting YouTube preview: {url}')

    # Extract video ID
    video_id = None

    if domain == 'youtu.be':
        video_id = url.split('/')[-1].split('?')[0]
    elif domain in ['youtube.com', 'youtube-nocookie.com', 'm.youtube.com']:
        parsed = urlparse(url)
        if parsed.path == '/watch':
            params = parse_qs(parsed.query)
            video_id = params.get('v', [None])[0]
        elif parsed.path.startswith('/embed/'):
            video_id = parsed.path.split('/embed/')[-1].split('?')[0]
        elif parsed.path.startswith('/v/'):
            video_id = parsed.path.split('/v/')[-1].split('?')[0]
        elif parsed.path.startswith('/movie/'):
            # YouTube Movies
            video_id = parsed.path.split('/movie/')[-1].split('?')[0]
        elif parsed.path.startswith('/music/'):
            # YouTube Music
            video_id = parsed.path.split('/music/')[-1].split('?')[0]

    if not video_id:
        return

    logger.debug(f'YouTube video ID: {video_id}')

    # Get video metadata from YouTube oEmbed API
    oembed_url = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json'

    try:
        data = http.get(oembed_url)

        if not data:
            return

        title = data.get('title', 'Unknown')
        author = data.get('author_name', 'Unknown')

        response = f"{formatter.bold(title)} | by {formatter.italic(author)}"
        bot.say(formatter.truncate(response, max_len=400))

    except Exception as e:
        logger.exception('Error fetching YouTube oEmbed data', e)


@plugin.url(r'https?://(?:www\.)?github\.com/.*')
def preview_github(bot, trigger):
    """Preview GitHub repositories, issues, actions, and gists."""
    url = trigger.group(0).strip()
    logger.info(f'Extracting GitHub preview: {url}')

    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]

    if len(path_parts) < 2:
        return

    owner = path_parts[0]
    repo = path_parts[1]

    # Handle different GitHub URL types
    if len(path_parts) == 2:
        # Repository
        preview_github_repo(bot, owner, repo)
    elif len(path_parts) >= 3:
        resource_type = path_parts[2]

        if resource_type == 'issues' and len(path_parts) >= 4:
            issue_num = path_parts[3]
            preview_github_issue(bot, owner, repo, issue_num)
        elif resource_type == 'pull' and len(path_parts) >= 4:
            pr_num = path_parts[3]
            preview_github_pr(bot, owner, repo, pr_num)
        elif resource_type == 'actions':
            preview_github_actions(bot, owner, repo)
        elif resource_type == 'gist':
            if len(path_parts) >= 3:
                gist_id = path_parts[2] if len(path_parts) == 3 else path_parts[-1]
                preview_github_gist(bot, gist_id)
        else:
            # Try repo as fallback
            preview_github_repo(bot, owner, repo)


def preview_github_repo(bot, owner: str, repo: str):
    """Preview GitHub repository."""
    api_url = f'https://api.github.com/repos/{owner}/{repo}'

    try:
        data = http.get(api_url)
        if not data:
            return

        name = data.get('full_name', f'{owner}/{repo}')
        description = data.get('description', '')
        stars = data.get('stargazers_count', 0)
        forks = data.get('forks_count', 0)
        language = data.get('language', '')
        private = data.get('private', False)

        response = f"{formatter.bold(name)}"
        if private:
            response += " {private}"
        if language:
            response += f" | {formatter.monospace(language)}"
        response += f" | stars: {formatter.underline(str(stars))} | forks: {formatter.underline(str(forks))}"

        bot.say(formatter.truncate(response, max_len=400))

        if description:
            desc = description[:200] if len(description) > 200 else description
            bot.say(formatter.truncate(desc, max_len=400))

    except Exception as e:
        logger.exception('Error fetching GitHub repo data', e)


def preview_github_issue(bot, owner: str, repo: str, issue_num: str):
    """Preview GitHub issue."""
    api_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}'

    try:
        data = http.get(api_url)
        if not data:
            return

        title = data.get('title', 'Unknown')
        state = data.get('state', 'unknown')
        user = data.get('user', {}).get('login', 'Unknown')
        comments = data.get('comments', 0)
        labels = [l.get('name', '') for l in data.get('labels', [])[:3]]

        response = f"{formatter.bold(f'#{formatter.underline(issue_num)}: {title}')} | {state} | by {formatter.italic(user)}"
        if comments > 0:
            response += f" | {formatter.underline(str(comments))} comments"
        bot.say(formatter.truncate(response, max_len=400))

        if labels:
            labels_str = ', '.join(labels)
            bot.say(formatter.truncate(f"Labels: {labels_str}", max_len=400))

    except Exception as e:
        logger.exception('Error fetching GitHub issue data', e)


def preview_github_pr(bot, owner: str, repo: str, pr_num: str):
    """Preview GitHub pull request."""
    api_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}'

    try:
        data = http.get(api_url)
        if not data:
            return

        title = data.get('title', 'Unknown')
        state = data.get('state', 'unknown')
        user = data.get('user', {}).get('login', 'Unknown')
        merged = data.get('merged', False)
        additions = data.get('additions', 0)
        deletions = data.get('deletions', 0)

        status = 'merged' if merged else state
        response = f"{formatter.bold(f'PR #{pr_num}: {title}')} | {status} | by {formatter.italic(user)}"
        if additions > 0 or deletions > 0:
            response += f" | +{formatter.underline(str(additions))} additions/-{formatter.underline(str(deletions))} deletions"
        bot.say(formatter.truncate(response, max_len=400))

    except Exception as e:
        logger.exception('Error fetching GitHub PR data', e)


def preview_github_actions(bot, owner: str, repo: str):
    """Preview GitHub Actions workflows."""
    api_url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows'

    try:
        data = http.get(api_url)
        if not data or 'workflows' not in data:
            return

        workflows = data.get('workflows', [])
        total = data.get('total_count', 0)

        response = f"{formatter.bold(f'{owner}/{repo}')} Actions | {formatter.underline(str(total))} workflow(s)"
        bot.say(formatter.truncate(response, max_len=400))

        # Show first few workflows
        for wf in workflows[:3]:
            wf_name = wf.get('name', 'Unknown')
            wf_state = wf.get('state', 'unknown')
            bot.say(formatter.truncate(f"  • {wf_name} ({wf_state})", max_len=400))

    except Exception as e:
        logger.exception('Error fetching GitHub Actions data', e)


def preview_github_gist(bot, gist_id: str):
    """Preview GitHub gist."""
    api_url = f'https://api.github.com/gists/{gist_id}'

    try:
        data = http.get(api_url)
        if not data:
            return

        description = data.get('description', '')
        owner = data.get('owner', {}).get('login', 'Unknown') if data.get('owner') else 'Anonymous'
        files = list(data.get('files', {}).keys())
        comments = data.get('comments', 0)
        data.get('forks', [])

        response = f"{formatter.bold('Gist')} by {formatter.italic(owner)}"
        if files:
            response += f" | {formatter.underline(str(len(files)))} file(s)"
        if comments > 0:
            response += f" | {formatter.underline(str(comments))} comments"
        bot.say(formatter.truncate(response, max_len=400))

        if description:
            desc = description[:200] if len(description) > 200 else description
            bot.say(formatter.truncate(desc, max_len=400))

        if files:
            files_str = ', '.join(files[:5])
            bot.say(formatter.truncate(f"Files: {files_str}", max_len=400))

    except Exception as e:
        logger.exception('Error fetching GitHub gist data', e)


@plugin.url(r'https?://(?:www\.)?gitlab\.com/.*')
def preview_gitlab(bot, trigger):
    """Preview GitLab repositories, issues, and snippets."""
    url = trigger.group(0).strip()
    preview_gitlab_impl(bot, trigger, url)


def preview_gitlab_impl(bot, trigger, url: str):
    """Preview GitLab repositories, issues, and snippets."""
    logger.info(f'Extracting GitLab preview: {url}')

    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]

    if len(path_parts) < 2:
        return

    # GitLab uses /group/subgroup/project format
    if len(path_parts) == 2:
        # Repository
        preview_gitlab_repo(bot, '/'.join(path_parts))
    elif len(path_parts) >= 3:
        resource_type = path_parts[-2]

        if resource_type == '-':
            # Repository (URL ends with /group/project)
            preview_gitlab_repo(bot, '/'.join(path_parts[:-1]))
        elif resource_type == 'issues' and path_parts[-1].isdigit():
            issue_id = path_parts[-1]
            project_path = '/'.join(path_parts[:-2])
            preview_gitlab_issue(bot, project_path, issue_id)
        elif resource_type == 'snippets' and path_parts[-1].isdigit():
            snippet_id = path_parts[-1]
            project_path = '/'.join(path_parts[:-2])
            preview_gitlab_snippet(bot, project_path, snippet_id)
        elif resource_type == '-':
            # Try repo
            preview_gitlab_repo(bot, '/'.join(path_parts[:-1]))


def preview_gitlab_repo(bot, project_path: str):
    """Preview GitLab repository."""
    encoded_path = '/'.join(http.quote(p) for p in project_path.split('/'))
    api_url = f'https://gitlab.com/api/v4/projects/{encoded_path}'

    try:
        data = http.get(api_url)
        if not data:
            return

        name = data.get('name_with_namespace', project_path)
        description = data.get('description', '')
        stars = data.get('star_count', 0)
        forks = data.get('forks_count', 0)
        visibility = data.get('visibility', 'private')

        response = f"{formatter.bold(name)} | {visibility}"
        response += f" | stars: {formatter.underline(str(stars))} | forks: {formatter.underline(str(forks))}"
        bot.say(formatter.truncate(response, max_len=400))

        if description:
            desc = description[:200] if len(description) > 200 else description
            bot.say(formatter.truncate(desc, max_len=400))

    except Exception as e:
        logger.exception('Error fetching GitLab repo data', e)


def preview_gitlab_issue(bot, project_path: str, issue_id: str):
    """Preview GitLab issue."""
    encoded_path = '/'.join(http.quote(p) for p in project_path.split('/'))
    api_url = f'https://gitlab.com/api/v4/projects/{encoded_path}/issues/{issue_id}'

    try:
        data = http.get(api_url)
        if not data:
            return

        title = data.get('title', 'Unknown')
        state = data.get('state', 'unknown')
        author = data.get('author', {}).get('username', 'Unknown')
        labels = [l.get('name', '') for l in data.get('labels', [])[:3]]

        response = f"{formatter.bold(f'#{issue_id}: {title}')} | {state} | by {formatter.italic(author)}"
        bot.say(formatter.truncate(response, max_len=400))

        if labels:
            labels_str = ', '.join(labels)
            bot.say(formatter.truncate(f"Labels: {labels_str}", max_len=400))

    except Exception as e:
        logger.exception('Error fetching GitLab issue data', e)


def preview_gitlab_snippet(bot, project_path: str, snippet_id: str):
    """Preview GitLab snippet."""
    encoded_path = '/'.join(http.quote(p) for p in project_path.split('/'))
    api_url = f'https://gitlab.com/api/v4/projects/{encoded_path}/snippets/{snippet_id}'

    try:
        data = http.get(api_url)
        if not data:
            return

        title = data.get('title', 'Unknown')
        author = data.get('author', {}).get('username', 'Unknown')
        visibility = data.get('visibility', 'private')
        files = data.get('files', [])

        response = f"{formatter.bold(title)} | by {formatter.italic(author)} | {visibility}"
        if files:
            response += f" | {formatter.underline(str(len(files)))} file(s)"
        bot.say(formatter.truncate(response, max_len=400))

    except Exception as e:
        logger.exception('Error fetching GitLab snippet data', e)


@plugin.url(r'https?://(?:i\.)?imgur\.com/.*')
def preview_imgur(bot, trigger):
    """Preview Imgur images and galleries."""
    url = trigger.group(0).strip()
    logger.info(f'Extracting Imgur preview: {url}')

    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]

    if not path_parts:
        return

    resource_type = path_parts[0]  # 'a' for album, 'gallery' for gallery, or image ID
    path_parts[1] if len(path_parts) > 1 else path_parts[0]

    if resource_type == 'a':
        # Album
        pass
    elif resource_type == 'gallery':
        # Gallery
        pass
    else:
        # Single image
        pass

    try:
        # Imgur API requires client ID, but we can try without (may fail)
        # For now, use OpenGraph as fallback
        preview_opengraph(bot, trigger, url, 'imgur.com')
    except Exception as e:
        logger.exception('Error fetching Imgur data', e)


@plugin.url(r'https?://(?:www\.|old\.|np\.)?reddit\.com/.*')
def preview_reddit(bot, trigger):
    """Preview Reddit posts and comments."""
    url = trigger.group(0).strip()
    logger.info(f'Extracting Reddit preview: {url}')

    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]

    if len(path_parts) < 2:
        return

    resource_type = path_parts[0]  # 'r' for subreddit, 'user' for user

    if resource_type == 'r' and len(path_parts) >= 3:
        subreddit = path_parts[1]
        post_id = path_parts[3] if len(path_parts) >= 4 else None

        if post_id:
            # Reddit post
            preview_reddit_post(bot, subreddit, post_id)
        else:
            # Subreddit
            preview_reddit_subreddit(bot, subreddit)
    else:
        # Try OpenGraph as fallback
        domain = parsed.netloc.lower().replace('www.', '')
        preview_opengraph(bot, trigger, url, domain)


def preview_reddit_post(bot, subreddit: str, post_id: str):
    """Preview Reddit post."""
    # Reddit JSON API: https://www.reddit.com/r/subreddit/comments/postid.json
    api_url = f'https://www.reddit.com/r/{subreddit}/comments/{post_id}.json'

    try:
        data = http.get(api_url)
        if not data or not isinstance(data, list) or len(data) < 1:
            return

        post_data = data[0]['data']['children'][0]['data']

        title = post_data.get('title', 'Unknown')
        author = post_data.get('author', 'Unknown')
        score = post_data.get('score', 0)
        comments = post_data.get('num_comments', 0)
        subreddit_name = post_data.get('subreddit', subreddit)
        url = post_data.get('url', '')
        selftext = post_data.get('selftext', '')

        response = f"{formatter.bold(title)} | r/{subreddit_name}"
        response += f" | by {formatter.italic(author)}"
        response += f" | {formatter.underline(str(score))} points | {formatter.underline(str(comments))} comments"
        bot.say(formatter.truncate(response, max_len=400))

        if selftext:
            text = selftext[:200] if len(selftext) > 200 else selftext
            bot.say(formatter.truncate(text, max_len=400))
        elif url and not url.startswith('https://reddit.com'):
            # External URL
            bot.say(formatter.monospace(url))

    except Exception as e:
        logger.exception('Error fetching Reddit post data', e)


def preview_reddit_subreddit(bot, subreddit: str):
    """Preview Reddit subreddit."""
    api_url = f'https://www.reddit.com/r/{subreddit}/about.json'

    try:
        data = http.get(api_url)
        if not data or 'data' not in data:
            return

        subreddit_data = data['data']

        display_name = subreddit_data.get('display_name', subreddit)
        title = subreddit_data.get('title', '')
        subscribers = subreddit_data.get('subscribers', 0)
        description = subreddit_data.get('public_description', '')

        response = f"{formatter.bold(f'r/{display_name}')}"
        if title:
            response += f" | {title}"
        response += f" | {formatter.underline(f'{subscribers:,}')} subscribers"
        bot.say(formatter.truncate(response, max_len=400))

        if description:
            desc = description[:200] if len(description) > 200 else description
            bot.say(formatter.truncate(desc, max_len=400))

    except Exception as e:
        logger.exception('Error fetching Reddit subreddit data', e)


@plugin.command('preview_add')
@plugin.require_privilege(plugin.OP, 'You must be a channel operator to manage preview whitelist.')
def preview_add(bot, trigger):
    """Add a regex pattern to the URL preview whitelist with optional field enable/disable.

    Usage: .preview_add <regex_pattern> [+og:field1] [-og:field2] ...
    Examples:
      .preview_add https://example\\.com/.*
      .preview_add https://news\\.com/.* +og:article:author -og:video
      .preview_add https://video\\.com/.* +og:video +og:image -og:description
    """
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .preview_add <regex_pattern> [+og:field] [-og:field] ...')
        bot.notice(trigger.nick, 'Example: .preview_add https://example\\.com/.* +og:image -og:video')
        return

    args = trigger.group(2).strip().split()
    pattern = args[0]
    enable_fields = []
    disable_fields = []

    # Parse +og:field and -og:field arguments
    for arg in args[1:]:
        if arg.startswith('+'):
            field = arg[1:].strip()
            if field.startswith('og:'):
                enable_fields.append(field)
            else:
                enable_fields.append(f'og:{field}')
        elif arg.startswith('-'):
            field = arg[1:].strip()
            if field.startswith('og:'):
                disable_fields.append(field)
            else:
                disable_fields.append(f'og:{field}')
        else:
            bot.notice(trigger.nick, f'Invalid argument "{arg}". Use +og:field to enable or -og:field to disable.')
            return

    # Validate regex
    try:
        re.compile(pattern)
    except re.error as e:
        bot.notice(trigger.nick, f'Invalid regex pattern: {e}')
        return

    whitelist = get_whitelist(bot)

    # Check if pattern already exists
    for entry in whitelist:
        if entry.get('pattern') == pattern:
            bot.notice(trigger.nick, f'Pattern "{pattern}" already in whitelist. Use .preview_remove first.')
            return

    # Add new entry
    entry = {
        'pattern': pattern,
        'enable_fields': enable_fields,
        'disable_fields': disable_fields
    }
    whitelist.append(entry)
    bot.memory['preview_whitelist'] = whitelist

    msg = f'Added "{pattern}" to preview whitelist'
    if enable_fields:
        msg += f' (enable: {", ".join(enable_fields)})'
    if disable_fields:
        msg += f' (disable: {", ".join(disable_fields)})'
    bot.notice(trigger.nick, msg + '.')


@plugin.command('preview_remove')
@plugin.require_privilege(plugin.OP, 'You must be a channel operator to manage preview whitelist.')
def preview_remove(bot, trigger):
    """Remove a regex pattern from the URL preview whitelist."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .preview_remove <regex_pattern>')
        return

    pattern = trigger.group(2).strip()
    whitelist = get_whitelist(bot)

    # Find and remove matching entry
    for i, entry in enumerate(whitelist):
        if entry.get('pattern') == pattern:
            whitelist.pop(i)
            bot.memory['preview_whitelist'] = whitelist
            bot.notice(trigger.nick, f'Removed "{pattern}" from preview whitelist.')
            return

    bot.notice(trigger.nick, f'Pattern "{pattern}" not found in whitelist.')


@plugin.command('preview_list')
@plugin.require_privilege(plugin.OP, 'You must be a channel operator to view preview whitelist.')
def preview_list(bot, trigger):
    """List all regex patterns in the URL preview whitelist with their field settings."""
    whitelist = get_whitelist(bot)
    if not whitelist:
        bot.notice(trigger.nick, 'Preview whitelist is empty.')
        return

    bot.notice(trigger.nick, 'Current preview whitelist patterns:')
    for i, entry in enumerate(whitelist, 1):
        pattern = entry.get('pattern', '')
        enable_fields = entry.get('enable_fields', [])
        disable_fields = entry.get('disable_fields', [])

        msg = f"{i}. {formatter.monospace(pattern)}"
        if enable_fields:
            msg += f" | enable: {', '.join(enable_fields)}"
        if disable_fields:
            msg += f" | disable: {', '.join(disable_fields)}"
        bot.say(msg)


def setup(bot):
    """Module setup - Preview module loaded."""
    bot.memory['preview_loaded'] = True
    if 'preview_whitelist' not in bot.memory:
        # Default whitelist for OpenGraph sites
        bot.memory['preview_whitelist'] = [
            {'pattern': r'https?://(?:www\.)?linkedin\.com/.*', 'enable_fields': [], 'disable_fields': []},
            {'pattern': r'https?://(?:www\.)?(?:twitter\.com|x\.com)/.*', 'enable_fields': [], 'disable_fields': []},
            {'pattern': r'https?://.*nitter.*/.*', 'enable_fields': [], 'disable_fields': []},
            {'pattern': r'https?://(?:www\.)?(?:snort\.social|damus\.io|iris\.to|amethyst\.social|nostr\.band|nostr\.com|nostr\.directory|nostrview\.com|coracle\.social|nostrgram\.co|zap\.stream|nostr\.land|primal\.net|nostr\.watch|nostr\.pics|nostr\.io|nostr\.org|nostr\.link|nostr\.pub|nostr\.social|nostr\.network|nostr\.me|nostr\.app|nostr\.tools|nostr\.space|nostr\.zone|nostr\.dev|nostr\.tech|nostr\.online|nostr\.site|nostr\.live|nostr\.news|nostr\.media|nostr\.info|nostr\.net|nostr\.xyz|nostr\.museum|nostr\.cloud|nostr\.web|nostr\.tv|nostr\.ws|nostr\.email)/.*', 'enable_fields': [], 'disable_fields': []},
            {'pattern': r'https?://(?:www\.)?nostr\..*/.*', 'enable_fields': [], 'disable_fields': []},
            {'pattern': r'nostr:.*', 'enable_fields': [], 'disable_fields': []},
        ]
    logger.info('Preview module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['preview_loaded'] = False
    logger.info('Preview module unloaded')

