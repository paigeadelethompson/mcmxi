"""
OpenGraph metadata extraction utilities.
"""
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # Optional dependency

import os

# Import HTTPClient from http_client module
import sys

from sopel.tools import get_logger

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from http_client import HTTPClient


# OpenGraph extraction utility
class OpenGraphExtractor:
    """Extract OpenGraph metadata from HTML content."""

    @staticmethod
    def extract(html_content: str, url: str = '') -> Dict[str, Any]:
        """
        Extract OpenGraph metadata from HTML content.
        Returns dict with all OG fields found, using og: prefix as keys.
        Also includes 'title', 'description', 'image', 'url', 'type', 'site_name' for compatibility.
        """
        if BeautifulSoup is None:
            logger = get_logger('opengraph')
            logger.error('BeautifulSoup not available. Install with: pip install beautifulsoup4 lxml')
            return {}

        result = {}
        images = []  # Collect multiple images
        videos = []  # Collect multiple videos
        audios = []  # Collect multiple audios

        try:
            soup = BeautifulSoup(html_content, 'lxml')

            # Extract all OpenGraph meta tags
            og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))

            for tag in og_tags:
                prop = tag.get('property', '')
                content = tag.get('content', '')

                if not prop or not content:
                    continue

                # Store all OG properties with full name
                result[prop] = content

                # Also store common fields without prefix for compatibility
                if prop == 'og:title':
                    result['title'] = content
                elif prop == 'og:description':
                    result['description'] = content
                elif prop == 'og:image':
                    if 'image' not in result:  # First image as primary
                        result['image'] = content
                    images.append(content)
                elif prop == 'og:image:url':
                    if 'image' not in result:
                        result['image'] = content
                    images.append(content)
                elif prop == 'og:image:secure_url':
                    if 'image' not in result:
                        result['image'] = content
                elif prop == 'og:url':
                    result['url'] = content
                elif prop == 'og:type':
                    result['type'] = content
                elif prop == 'og:site_name':
                    result['site_name'] = content
                elif prop in ('og:video', 'og:video:url'):
                    videos.append(content)
                elif prop in ('og:audio', 'og:audio:url'):
                    audios.append(content)

            # Store arrays for multiple media items
            if images:
                result['images'] = images
            if videos:
                result['videos'] = videos
            if audios:
                result['audios'] = audios

            # Fallback to regular meta tags if OpenGraph not found
            if 'title' not in result:
                title_tag = soup.find('title')
                if title_tag:
                    title_text = title_tag.get_text(strip=True)
                    result['title'] = title_text
                    result['og:title'] = title_text

            if 'description' not in result:
                desc_tag = soup.find('meta', attrs={'name': 'description'})
                if desc_tag:
                    desc_content = desc_tag.get('content', '')
                    result['description'] = desc_content
                    result['og:description'] = desc_content

            # Make image URLs absolute if relative
            def make_absolute(url_str: str, base_url: str) -> str:
                if not url_str or not base_url:
                    return url_str
                if url_str.startswith('//'):
                    parsed = urlparse(base_url)
                    return f"{parsed.scheme}:{url_str}"
                elif url_str.startswith('/'):
                    return urljoin(base_url, url_str)
                return url_str

            if url:
                # Make all image URLs absolute
                if 'image' in result:
                    result['image'] = make_absolute(result['image'], url)
                if 'og:image' in result:
                    result['og:image'] = make_absolute(result['og:image'], url)
                if 'images' in result:
                    result['images'] = [make_absolute(img, url) for img in result['images']]
                for key in list(result.keys()):
                    if key.startswith('og:image') and key not in ['og:image', 'og:image:url', 'og:image:secure_url']:
                        # Skip nested properties that aren't URLs
                        if 'url' in key or 'secure_url' in key:
                            result[key] = make_absolute(result[key], url)

            # Use provided URL as fallback
            if 'url' not in result and url:
                result['url'] = url
                result['og:url'] = url

        except Exception as e:
            logger = get_logger('opengraph')
            logger.exception('Error extracting OpenGraph data', e)

        return result

    @staticmethod
    def extract_from_url(url: str, http_client: Optional[Any] = None, max_size: int = 1024 * 1024) -> Dict[str, Any]:
        """
        Extract OpenGraph metadata from a URL.
        Uses provided HTTPClient or creates a default one.
        Returns dict with all OpenGraph fields or empty dict on error.
        """
        if http_client is None:
            http_client = HTTPClient(max_size=max_size)

        try:
            # Get HTML content
            html_content = http_client.get_text(url)
            if not html_content:
                return {}

            return OpenGraphExtractor.extract(html_content, url)

        except Exception as e:
            logger = get_logger('opengraph')
            logger.exception(f'Error extracting OpenGraph from URL: {url}', e)
            return {}

