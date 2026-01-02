"""
API registry for module API lists.
Note: Plugin commands are in common.py since it's the Sopel-loaded module.
"""
from typing import Any, Dict, List, Optional

from sopel.tools import get_logger

# API registry for module API lists
_API_REGISTRY = {}


def register_apis(category: str, apis: List[Dict[str, Any]]):
    """
    Register an APIS array for a category.
    Modules should call this in their setup() function.

    Args:
        category: Category name (e.g., 'animals', 'weather')
        apis: List of API dictionaries with 'name', 'description', 'link', 'https', 'cors' keys
    """
    _API_REGISTRY[category.lower()] = {
        'apis': apis,
        'category': category
    }
    logger = get_logger('api_registry')
    logger.debug(f'Registered {len(apis)} APIs for category: {category}')


def get_apis(category: str) -> Optional[Dict[str, Any]]:
    """Get registered APIs for a category. Returns dict with 'apis' and 'category' keys."""
    return _API_REGISTRY.get(category.lower())


def get_api_registry():
    """Get the internal API registry dictionary. Used by common.py for plugin commands."""
    return _API_REGISTRY


def apis_list_command(bot, trigger):
    """List all registered API categories or APIs in a specific category."""
    api_registry = get_api_registry()
    if not trigger.group(2):
        # List all categories
        categories = sorted(api_registry.keys())
        if not categories:
            bot.say('No API categories registered')
            return
        bot.say(f'Available API categories ({len(categories)}): {", ".join(categories)}')
        bot.say('Use {prefix}apis <category> to list APIs in a category')
        return

    category = trigger.group(2).strip().lower()
    category_data = get_apis(category)

    if not category_data:
        bot.notice(trigger.nick, f'Category not found: {category}')
        bot.notice(trigger.nick, f'Available categories: {", ".join(sorted(api_registry.keys()))}')
        return

    apis = category_data['apis']
    cat_name = category_data['category']
    max_show = 10

    bot.say(f'Available {cat_name} APIs ({len(apis)}):')
    for i, api in enumerate(apis[:max_show], 1):
        desc = api.get('description', '')[:50]
        bot.say(f"{i}. {api.get('name', 'Unknown')} - {desc}")
    if len(apis) > max_show:
        bot.say(f'... and {len(apis) - max_show} more. Use {prefix}api_info <category> <name> for details')


def api_info_command(bot, trigger):
    """Get information about a specific API. Usage: `api_info <category> <api_name>"""
    api_registry = get_api_registry()
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `api_info <category> <api_name>')
        return

    args = trigger.group(2).strip().split(None, 1)
    if len(args) < 2:
        bot.notice(trigger.nick, 'Usage: `api_info <category> <api_name>')
        return

    category = args[0].lower()
    search_name = args[1].lower()

    category_data = get_apis(category)
    if not category_data:
        bot.notice(trigger.nick, f'Category not found: {category}')
        bot.notice(trigger.nick, f'Available categories: {", ".join(sorted(api_registry.keys()))}')
        return

    apis = category_data['apis']
    for api in apis:
        if search_name in api.get('name', '').lower():
            name = api.get('name', 'Unknown')
            desc = api.get('description', 'No description')
            link = api.get('link', 'N/A')
            https = api.get('https', False)
            cors = api.get('cors', 'unknown')
            bot.say(f"{name}: {desc}")
            bot.say(f"Link: {link} | HTTPS: {https} | CORS: {cors}")
            return

    bot.notice(trigger.nick, f'API not found: {args[1]} in category {category}')


def api_search_command(bot, trigger):
    """Search APIs by name or description. Usage: `api_search <category> <query>"""
    api_registry = get_api_registry()
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `api_search <category> <query>')
        return

    args = trigger.group(2).strip().split(None, 1)
    if len(args) < 2:
        bot.notice(trigger.nick, 'Usage: `api_search <category> <query>')
        return

    category = args[0].lower()
    query = args[1].lower()

    category_data = get_apis(category)
    if not category_data:
        bot.notice(trigger.nick, f'Category not found: {category}')
        bot.notice(trigger.nick, f'Available categories: {", ".join(sorted(api_registry.keys()))}')
        return

    apis = category_data['apis']
    results = []
    for api in apis:
        name = api.get('name', '').lower()
        desc = api.get('description', '').lower()
        if query in name or query in desc:
            results.append(api)

    if not results:
        bot.notice(trigger.nick, f'No APIs found matching: {args[1]} in category {category}')
        return

    max_results = 5
    bot.say(f'Found {len(results)} API(s):')
    for api in results[:max_results]:
        name = api.get('name', 'Unknown')
        desc = api.get('description', '')[:60]
        bot.say(f"- {name}: {desc}")
    if len(results) > max_results:
        bot.say(f'... and {len(results) - max_results} more results')

