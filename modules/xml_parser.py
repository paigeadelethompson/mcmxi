"""
XML parsing utilities using ElementTree and BeautifulSoup.
"""
from typing import Any, List, Optional
from xml.etree import ElementTree as ET

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # Optional dependency

from sopel.tools import get_logger


# XML parsing utility
class XMLParser:
    """XML parsing utilities using ElementTree and BeautifulSoup."""

    @staticmethod
    def parse_etree(xml_string: str) -> Optional[ET.Element]:
        """Parse XML string using ElementTree. Returns root element or None."""
        try:
            return ET.fromstring(xml_string)
        except ET.ParseError as e:
            logger = get_logger('xml_parser')
            logger.exception(f'XML parse error: {e}')
            return None
        except Exception as e:
            logger = get_logger('xml_parser')
            logger.exception('Error parsing XML', e)
            return None

    @staticmethod
    def parse_bs4(xml_string: str, parser: str = 'xml') -> Optional[Any]:
        """Parse XML/HTML string using BeautifulSoup. Returns BeautifulSoup object or None."""
        if BeautifulSoup is None:
            logger = get_logger('xml_parser')
            logger.error('BeautifulSoup not available. Install with: pip install beautifulsoup4 lxml')
            return None
        try:
            return BeautifulSoup(xml_string, parser)
        except Exception as e:
            logger = get_logger('xml_parser')
            logger.exception('Error parsing XML with BeautifulSoup', e)
            return None

    @staticmethod
    def find_all_text(root: Any, tag: str) -> List[str]:
        """Find all text content of elements with given tag using ElementTree."""
        if root is None:
            return []
        return [elem.text.strip() for elem in root.findall(f'.//{tag}') if elem.text]

    @staticmethod
    def find_text(root: Any, tag: str, default: str = '') -> str:
        """Find first text content of element with given tag using ElementTree."""
        if root is None:
            return default
        elem = root.find(f'.//{tag}')
        return elem.text.strip() if elem is not None and elem.text else default

    @staticmethod
    def find_all_bs4(soup: Any, tag: str) -> List[str]:
        """Find all text content of elements with given tag using BeautifulSoup."""
        if soup is None or BeautifulSoup is None:
            return []
        return [elem.get_text(strip=True) for elem in soup.find_all(tag)]

    @staticmethod
    def find_one_bs4(soup: Any, tag: str, default: str = '') -> str:
        """Find first text content of element with given tag using BeautifulSoup."""
        if soup is None or BeautifulSoup is None:
            return default
        elem = soup.find(tag)
        return elem.get_text(strip=True) if elem else default

