"""
Sopel module for Books APIs.
Supports 16 public APIs with no authentication required.
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
        'name': 'Bhagavad Gita telugu',
        'description': 'Bhagavad Gita API in telugu and odia languages',
        'link': 'https://gita-api.vercel.app',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Bible-api',
        'description': 'Free Bible API with multiple languages',
        'link': 'https://bible-api.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Crossref Metadata Search',
        'description': 'Books & Articles Metadata',
        'link': 'https://github.com/CrossRef/rest-api-doc',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Gutendex',
        'description': 'Web-API for fetching data from Project Gutenberg Books Library',
        'link': 'https://gutendex.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Harry Potter',
        'description': 'API to get data from Harry Potter books, movies and characters',
        'link': 'https://github.com/fedeperin/potterapi',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Library Management',
        'description': 'Manage users, books, authors, loans and reviews',
        'link': 'https://github.com/adam-dev2/library-management-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Open Library',
        'description': 'Books, book covers and related data',
        'link': 'https://openlibrary.org/developers/api',
        'https': True,
        'cors': 'no',
    },
    {
        'name': 'Penguin Publishing',
        'description': 'Books, book covers and related data',
        'link': 'http://www.penguinrandomhouse.biz/webservices/rest/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'PoetryDB',
        'description': 'Enables you to get instant data from our vast poetry collection',
        'link': 'https://github.com/thundercomb/poetrydb#readme',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Quran',
        'description': 'RESTful Quran API with multiple languages',
        'link': 'https://quran.api-docs.io/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Quran Cloud',
        'description': 'A RESTful Quran API to retrieve an Ayah, Surah, Juz or the entire Holy Quran',
        'link': 'https://alquran.cloud/api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Quran-api',
        'description': 'Free Quran API Service with 90+ different languages and 400+ translations',
        'link': 'https://github.com/fawazahmed0/quran-api#readme',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Stephen King',
        'description': 'The varied works and characters of the prolific author Stephen King',
        'link': 'https://stephen-king-api.onrender.com/',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Thirukkural',
        'description': '1330 Thirukkural poems and explanation in Tamil and English',
        'link': 'https://api-thirukkural.web.app/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Wizard World',
        'description': 'Get information from the Harry Potter universe',
        'link': 'https://wizard-world-api.herokuapp.com/swagger/index.html',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Wolne Lektury',
        'description': 'API for obtaining information about e-books available on the WolneLektury.pl website',
        'link': 'https://wolnelektury.pl/api/',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('books')
@plugin.command('books')
@plugin.example(f'.books')
def books_list(bot, trigger):
    """List all available Books APIs."""
    bot.say(f'Available Books APIs (16):')
    for i, api in enumerate(APIS[:10], 1):  # Show first 10
        bot.say(f"{i}. {api['name']} - {api['description'][:50]}")
    if len(APIS) > 10:
        bot.say(f'... and {len(APIS) - 10} more. Use .books_info <name> for details')


@plugin.command('books_info')
@plugin.example(f'.books_info <name>')
def books_info(bot, trigger):
    """Get information about a specific Books API."""
    if not trigger.group(2):
        bot.say(f'Usage: .books_info <api_name>')
        return

    search_name = trigger.group(2).strip().lower()
    for api in APIS:
        if search_name in api['name'].lower():
            bot.say(f"{api['name']}: {api['description']}")
            bot.say(f"Link: {api['link']} | HTTPS: {api['https']} | CORS: {api['cors']}")
            return

    bot.say(f'API not found: {trigger.group(2)}')


@plugin.command('books_search')
@plugin.example(f'.books_search <query>')
def books_search(bot, trigger):
    """Search Books APIs by name or description."""
    if not trigger.group(2):
        bot.say(f'Usage: .books_search <query>')
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


@plugin.command('book_gutendex')
@plugin.example('.book_gutendex moby dick')
@plugin.example('.book_gutendex 2701')
def book_gutendex(bot, trigger):
    """Search for books using Gutendex (Project Gutenberg) API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .book_gutendex <title> or .book_gutendex <book_id>')
        return
    
    query = trigger.group(2).strip()
    logger.info(f'Book search: {query}')
    
    # Check if it's a numeric ID
    if query.isdigit():
        get_book_by_id(bot, trigger.nick, int(query))
    else:
        search_books(bot, trigger.nick, query)


def search_books(bot, nick: str, query: str):
    """Search for books by title."""
    encoded_query = http.quote(query)
    url = f'https://gutendex.com/books/?search={encoded_query}&limit=3'
    
    logger.debug(f'Searching books: {url}')
    data = http.get(url)
    
    if not data or 'results' not in data:
        bot.notice(nick, 'No books found or API error. Please try again.')
        return
    
    results = data.get('results', [])[:3]
    
    if not results:
        bot.notice(nick, f'No books found for "{query}"')
        return
    
    bot.say(f'Found {len(results)} book(s) for "{query}":')
    for book in results:
        title = book.get('title', 'Unknown')
        authors = ', '.join([a.get('name', '') for a in book.get('authors', [])])
        book_id = book.get('id', '')
        
        response = f"{formatter.bold(title)}"
        if authors:
            response += f" by {formatter.italic(authors)}"
        if book_id:
            response += f" | ID: {formatter.monospace(str(book_id))}"
        
        bot.say(formatter.truncate(response, max_len=400))


def get_book_by_id(bot, nick: str, book_id: int):
    """Get book details by Gutenberg ID."""
    url = f'https://gutendex.com/books/{book_id}/'
    
    logger.debug(f'Fetching book by ID: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(nick, f'Book with ID {book_id} not found.')
        return
    
    title = data.get('title', 'Unknown')
    authors = ', '.join([a.get('name', '') for a in data.get('authors', [])])
    languages = ', '.join(data.get('languages', []))
    download_count = data.get('download_count', 0)
    
    response = f"{formatter.bold(title)}"
    if authors:
        response += f" by {formatter.italic(authors)}"
    if languages:
        response += f" | Language: {formatter.monospace(languages)}"
    response += f" | Downloads: {formatter.bold(f'{download_count:,}')}"
    
    bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Books APIs loaded."""
    bot.memory['books_loaded'] = True
    bot.memory['books_count'] = 16
    logger.info('Books module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['books_loaded'] = False
    logger.info('Books module unloaded')


@plugin.command('book_openlibrary')
@plugin.example('.book_openlibrary python programming')
def book_openlibrary(bot, trigger):
    """Search for books using Open Library API."""
    # Open Library: https://openlibrary.org/developers/api
    # Endpoint: GET https://openlibrary.org/search.json?q={query}&limit=3
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .book_openlibrary <search_query>')
        bot.notice(trigger.nick, 'Example: .book_openlibrary python programming')
        return
    
    query = trigger.group(2).strip()
    
    logger.info(f'Open Library search: {query}')
    
    encoded_query = http.quote(query)
    url = f'https://openlibrary.org/search.json?q={encoded_query}&limit=3'
    
    logger.debug(f'Searching Open Library: {url}')
    data = http.get(url)
    
    if not data or 'docs' not in data:
        bot.notice(trigger.nick, 'Failed to search Open Library.')
        return
    
    docs = data.get('docs', [])
    num_found = data.get('numFound', 0)
    
    if not docs:
        bot.notice(trigger.nick, f'No books found for "{query}"')
        return
    
    bot.say(f'Found {num_found:,} book(s) for "{query}" (showing {len(docs)}):')
    for book in docs:
        title = book.get('title', 'Unknown')
        authors = book.get('author_name', [])
        author_str = ', '.join(authors[:2]) if authors else 'Unknown'
        if len(authors) > 2:
            author_str += f' +{len(authors)-2}'
        year = book.get('first_publish_year', '')
        
        response = f"{formatter.bold(title)}"
        response += f" by {formatter.italic(author_str)}"
        if year:
            response += f" | {formatter.monospace(str(year))}"
        
        bot.say(formatter.truncate(response, max_len=400))


@plugin.command('verse_bibleapi')
@plugin.example('.verse_bibleapi john 3:16')
@plugin.example('.verse_bibleapi random')
@plugin.example('.verse_bibleapi random JHN')
@plugin.example('.verse_bibleapi books')
def verse_bibleapi(bot, trigger):
    """Get Bible verse using Bible-api.com. Supports random verses and book listing."""
    # Bible-api: https://bible-api.com/
    # Endpoints:
    #   GET https://bible-api.com/{book}+{chapter}:{verse} - specific verse
    #   GET https://bible-api.com/data/web/random - random verse
    #   GET https://bible-api.com/data/web/random/{BOOK_ID} - random from book
    #   GET https://bible-api.com/data/web - list all books
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .verse_bibleapi <book> <chapter>:<verse> | random [book_id] | books')
        bot.notice(trigger.nick, 'Examples: .verse_bibleapi john 3:16')
        bot.notice(trigger.nick, '          .verse_bibleapi random')
        bot.notice(trigger.nick, '          .verse_bibleapi random JHN')
        bot.notice(trigger.nick, '          .verse_bibleapi books')
        return
    
    query = trigger.group(2).strip().lower()
    
    # Handle random verse
    if query.startswith('random'):
        parts = query.split()
        book_id = parts[1].upper() if len(parts) > 1 else None
        
        logger.info(f'Bible API random verse: {book_id or "all"}')
        
        if book_id:
            url = f'https://bible-api.com/data/web/random/{http.quote(book_id)}'
        else:
            url = 'https://bible-api.com/data/web/random'
        
        logger.debug(f'Fetching random verse: {url}')
        data = http.get(url)
        
        if not data or 'random_verse' not in data:
            bot.notice(trigger.nick, 'Failed to fetch random verse.')
            return
        
        verse_data = data.get('random_verse', {})
        translation = data.get('translation', {})
        translation_name = translation.get('name', 'WEB')
        
        book = verse_data.get('book', 'Unknown')
        chapter = verse_data.get('chapter', '')
        verse = verse_data.get('verse', '')
        text = verse_data.get('text', '').strip()
        
        reference = f"{book} {chapter}:{verse}"
        
        # Format verse (limit length)
        text_short = text[:300] if len(text) > 300 else text
        if len(text) > 300:
            text_short += '...'
        
        response = f"{formatter.bold('Random Verse')}: {formatter.bold(reference)} ({formatter.monospace(translation_name)}):"
        bot.say(response)
        bot.say(f"{formatter.italic(text_short)}")
        return
    
    # Handle book listing
    if query == 'books' or query == 'list':
        logger.info('Bible API list books')
        
        url = 'https://bible-api.com/data/web'
        
        logger.debug(f'Fetching books list: {url}')
        data = http.get(url)
        
        if not data or 'books' not in data:
            bot.notice(trigger.nick, 'Failed to fetch books list.')
            return
        
        translation = data.get('translation', {})
        translation_name = translation.get('name', 'WEB')
        books = data.get('books', [])
        
        if not books:
            bot.notice(trigger.nick, 'No books found.')
            return
        
        bot.say(f'{formatter.bold("Bible Books")} ({formatter.monospace(translation_name)}): {len(books)} books')
        
        # Show first 15 books
        book_list = ', '.join([f"{book.get('name', 'Unknown')} ({formatter.monospace(book.get('id', ''))})" for book in books[:15]])
        bot.say(book_list)
        
        if len(books) > 15:
            bot.say(f'... and {len(books) - 15} more books. Use .verse_bibleapi <book_id> <chapter>:<verse> for verses')
        return
    
    # Handle specific verse lookup
    reference = trigger.group(2).strip()
    
    logger.info(f'Bible API lookup: {reference}')
    
    # Clean up the reference (remove spaces, make lowercase)
    ref_clean = reference.replace(' ', '+').lower()
    url = f'https://bible-api.com/{ref_clean}'
    
    logger.debug(f'Fetching verse: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, f'Failed to fetch verse: {reference}')
        return
    
    text = data.get('text', '').strip()
    reference_full = data.get('reference', reference)
    translation = data.get('translation', 'KJV')
    translation_name = data.get('translation_name', translation)
    
    if not text:
        bot.notice(trigger.nick, f'Verse not found: {reference}')
        return
    
    # Format verse (limit length)
    text_short = text[:300] if len(text) > 300 else text
    if len(text) > 300:
        text_short += '...'
    
    response = f"{formatter.bold(reference_full)} ({formatter.monospace(translation_name)}):"
    bot.say(response)
    bot.say(f"{formatter.italic(text_short)}")


@plugin.command('poem_poetrydb')
@plugin.example('.poem_poetrydb author=emily+dickinson')
@plugin.example('.poem_poetrydb title=hope')
def poem_poetrydb(bot, trigger):
    """Search for poems using PoetryDB API."""
    # PoetryDB: https://github.com/thundercomb/poetrydb#readme
    # Endpoint: GET https://poetrydb.org/{endpoint}
    # Examples: /author/{author}, /title/{title}, /author,title/{author};{title}
    
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .poem_poetrydb <query>')
        bot.notice(trigger.nick, 'Examples: .poem_poetrydb author=emily+dickinson')
        bot.notice(trigger.nick, '          .poem_poetrydb title=hope')
        return
    
    query = trigger.group(2).strip()
    
    logger.info(f'PoetryDB search: {query}')
    
    # Parse query format: author=name or title=name
    if '=' in query:
        param, value = query.split('=', 1)
        param = param.strip().lower()
        value = value.strip()
        
        if param == 'author':
            endpoint = f'author/{http.quote(value)}'
        elif param == 'title':
            endpoint = f'title/{http.quote(value)}'
        else:
            bot.notice(trigger.nick, 'Query format: author=<name> or title=<name>')
            return
    else:
        # Default to title search
        endpoint = f'title/{http.quote(query)}'
    
    url = f'https://poetrydb.org/{endpoint}'
    
    logger.debug(f'Searching PoetryDB: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to search PoetryDB.')
        return
    
    # Response can be a list or object
    poems = data if isinstance(data, list) else [data] if data else []
    
    if not poems:
        bot.notice(trigger.nick, f'No poems found for "{query}"')
        return
    
    # Show first poem
    poem = poems[0]
    title = poem.get('title', 'Unknown')
    author = poem.get('author', 'Unknown')
    lines = poem.get('lines', [])
    
    response = f"{formatter.bold(title)} by {formatter.italic(author)}"
    bot.say(response)
    
    if lines:
        # Show first few lines
        poem_text = ' '.join(lines[:3])
        if len(lines) > 3:
            poem_text += '...'
        bot.say(f"{formatter.italic(poem_text[:250])}")


@plugin.command('book_stephenking')
@plugin.example('.book_stephenking')
@plugin.example('.book_stephenking random')
def book_stephenking(bot, trigger):
    """Get Stephen King book information."""
    # Stephen King API: https://stephen-king-api.onrender.com/
    # Endpoint: GET https://stephen-king-api.onrender.com/api/books
    
    logger.info('Stephen King book lookup')
    
    # For now, get list of books
    url = 'https://stephen-king-api.onrender.com/api/books'
    
    logger.debug(f'Fetching Stephen King books: {url}')
    data = http.get(url)
    
    if not data:
        bot.notice(trigger.nick, 'Failed to fetch Stephen King books.')
        return
    
    # Response can be a list or object
    books = data if isinstance(data, list) else data.get('data', []) if isinstance(data, dict) else []
    
    if not books:
        bot.notice(trigger.nick, 'No books found.')
        return
    
    # Show first 3 books
    bot.say(f'{formatter.bold("Stephen King Books")} (showing {min(3, len(books))}):')
    for book in books[:3]:
        title = book.get('title', book.get('Title', 'Unknown'))
        year = book.get('year', book.get('Year', ''))
        pages = book.get('pages', book.get('Pages', ''))
        
        response = f"{formatter.bold(title)}"
        if year:
            response += f" ({formatter.monospace(str(year))})"
        if pages:
            response += f" | {formatter.monospace(f'{pages} pages')}"
        bot.say(formatter.truncate(response, max_len=400))
