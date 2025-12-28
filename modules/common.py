"""
Utility modules for Sopel bot - logger, HTTP client, formatting, permissions, XML parsing.
"""
import json
import time
import urllib.request
import urllib.error
import socket
import ipaddress
import ssl
import http.client
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse, quote, urlencode, urljoin
from collections import defaultdict
from xml.etree import ElementTree as ET

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # Optional dependency

from sopel import plugin
from sopel.tools import get_logger

# Logger utility
def get_module_logger(name: str):
    """Get a logger for a module."""
    return get_logger(name)


# DNS resolution utilities
_anycast_resolver = None


def _get_anycast_resolver():
    """Get anycast DoTLS resolver from dns module."""
    global _anycast_resolver
    if _anycast_resolver is None:
        try:
            import sys
            import os
            dns_module_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dns_module.py')
            if os.path.exists(dns_module_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("dns_module", dns_module_path)
                dns_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(dns_module)
                _anycast_resolver = getattr(dns_module, 'anycast_resolver', None)
        except Exception as e:
            logger = get_logger('dns_resolver')
            logger.warning(f'Could not load anycast resolver: {e}')
    return _anycast_resolver


def validate_ip_address(ip_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate IP address is not private/reserved/multicast.
    For IPv6, only allows 2000::/3 (global unicast).
    Returns (is_valid, error_message).
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        
        if isinstance(ip, ipaddress.IPv4Address):
            # Check IPv4 private/reserved ranges
            if ip.is_private:
                return False, f'IPv4 address {ip_str} is private (RFC 1918)'
            if ip.is_loopback:
                return False, f'IPv4 address {ip_str} is loopback'
            if ip.is_link_local:
                return False, f'IPv4 address {ip_str} is link-local'
            if ip.is_multicast:
                return False, f'IPv4 address {ip_str} is multicast'
            if ip.is_reserved:
                return False, f'IPv4 address {ip_str} is reserved'
            # Check reserved range 240.0.0.0/4
            if ipaddress.ip_address(ip_str) in ipaddress.ip_network('240.0.0.0/4'):
                return False, f'IPv4 address {ip_str} is in reserved range 240.0.0.0/4'
        
        elif isinstance(ip, ipaddress.IPv6Address):
            # For IPv6, only allow 2000::/3 (global unicast)
            if ip not in ipaddress.ip_network('2000::/3'):
                return False, f'IPv6 address {ip_str} is not in global unicast range (2000::/3)'
        
        return True, None
        
    except ValueError:
        return False, f'Invalid IP address format: {ip_str}'


def resolve_hostname_dot(hostname: str) -> Optional[str]:
    """
    Resolve hostname using anycast DoTLS resolver.
    Returns first valid IP address or None on error.
    Tries A (IPv4) first, then AAAA (IPv6).
    Validates IPs are not private/reserved/multicast.
    For IPv6, only allows 2000::/3 (global unicast).
    """
    resolver = _get_anycast_resolver()
    if not resolver:
        # Fallback to system DNS if resolver not available, but still validate IPs
        try:
            addrinfo = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            for family, socktype, proto, canonname, sockaddr in addrinfo:
                ip = sockaddr[0]
                is_valid, error = validate_ip_address(ip)
                if is_valid:
                    return ip
            return None
        except Exception:
            return None
    
    # Try A record (IPv4) first
    try:
        from dns import rdatatype
        response = resolver.query(hostname, 'A')
        if response and hasattr(response, 'answer'):
            for rrset in response.answer:
                if rrset.rdtype == rdatatype.A:
                    for rdata in rrset:
                        ip = str(rdata.address)
                        is_valid, error = validate_ip_address(ip)
                        if is_valid:
                            return ip
    except Exception as e:
        logger = get_logger('dns_resolver')
        logger.debug(f'IPv4 resolution failed for {hostname}: {e}')
    
    # Try AAAA record (IPv6)
    try:
        from dns import rdatatype
        response = resolver.query(hostname, 'AAAA')
        if response and hasattr(response, 'answer'):
            for rrset in response.answer:
                if rrset.rdtype == rdatatype.AAAA:
                    for rdata in rrset:
                        ip = str(rdata.address)
                        is_valid, error = validate_ip_address(ip)
                        if is_valid:
                            return ip
    except Exception as e:
        logger = get_logger('dns_resolver')
        logger.debug(f'IPv6 resolution failed for {hostname}: {e}')
    
    return None


# Custom HTTPS handler that sets TLS hostname for SNI
class CustomHTTPSHandler(urllib.request.HTTPSHandler):
    """HTTPS handler that sets TLS hostname (SNI) to original hostname when connecting to IP."""
    
    def __init__(self, tls_hostname=None):
        self.tls_hostname = tls_hostname
        context = ssl.create_default_context()
        super().__init__(context=context)
    
    def https_open(self, req):
        """Open HTTPS connection with custom TLS hostname."""
        return self.do_open(self._make_connection, req)
    
    def _make_connection(self, host, port=443, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, **kwargs):
        """Create HTTPS connection with TLS hostname set to original hostname."""
        sock = socket.create_connection((host, port), timeout)
        context = self._context
        if self.tls_hostname:
            # Set server_hostname for SNI to original hostname
            ssock = context.wrap_socket(sock, server_hostname=self.tls_hostname)
        else:
            ssock = context.wrap_socket(sock)
        # Return connection with wrapped socket
        conn = http.client.HTTPSConnection(host, port=port, timeout=timeout)
        conn.sock = ssock
        return conn


# HTTP Client utility
class HTTPClient:
    """
    HTTP client with max filesize limit, rate limiting, backoff retry, and cooldown.
    """
    
    def __init__(self, max_size: int = 10 * 1024 * 1024,  # 10MB default
                 rate_limit: int = 60,  # requests per minute per domain
                 cooldown: float = 1.0,  # seconds between requests to same domain
                 max_retries: int = 3,  # max retry attempts
                 backoff_base: float = 2.0):  # exponential backoff base
        """Initialize HTTP client with rate limiting and retry settings."""
        self.max_size = max_size
        self.rate_limit = rate_limit
        self.cooldown = cooldown
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.logger = get_logger('http_client')
        
        # Rate limiting: track requests per domain
        self.request_times = defaultdict(list)  # domain -> list of timestamps
        
        # Cooldown: track last request time per domain
        self.last_request = {}  # domain -> timestamp
        
        # Retry tracking: track retry attempts per URL
        self.retry_counts = defaultdict(int)  # url -> retry count
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc or parsed.path.split('/')[0]
        except Exception:
            return 'unknown'
    
    @staticmethod
    def quote(text: str, safe: str = '/') -> str:
        """URL encode a string. Use this instead of urllib.parse.quote."""
        return quote(text, safe=safe)
    
    @staticmethod
    def urlencode(params: Dict[str, str]) -> str:
        """URL encode parameters. Use this instead of urllib.parse.urlencode."""
        return urlencode(params)
    
    def _check_rate_limit(self, domain: str) -> bool:
        """Check if request is within rate limit."""
        now = time.time()
        # Remove requests older than 1 minute
        self.request_times[domain] = [
            t for t in self.request_times[domain] if now - t < 60
        ]
        
        if len(self.request_times[domain]) >= self.rate_limit:
            self.logger.warning(f'Rate limit exceeded for {domain}: {len(self.request_times[domain])}/{self.rate_limit} requests/min')
            return False
        return True
    
    def _wait_cooldown(self, domain: str):
        """Wait for cooldown period if needed."""
        if domain in self.last_request:
            elapsed = time.time() - self.last_request[domain]
            if elapsed < self.cooldown:
                wait_time = self.cooldown - elapsed
                self.logger.debug(f'Cooldown: waiting {wait_time:.2f}s for {domain}')
                time.sleep(wait_time)
    
    def _should_retry(self, url: str, error: Exception) -> bool:
        """Determine if request should be retried."""
        if self.retry_counts[url] >= self.max_retries:
            return False
        
        # Retry on network errors and 5xx server errors
        if isinstance(error, urllib.error.HTTPError):
            return 500 <= error.code < 600
        elif isinstance(error, urllib.error.URLError):
            return True
        
        return False
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        return min(self.backoff_base ** attempt, 60)  # Cap at 60 seconds
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, 
            timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Make a GET request with rate limiting, cooldown, and retry logic.
        Returns JSON response or None on error.
        """
        domain = self._get_domain(url)
        
        # Check rate limit
        if not self._check_rate_limit(domain):
            self.logger.warning(f'Rate limit exceeded for {domain}, request denied')
            return None
        
        # Wait for cooldown
        self._wait_cooldown(domain)
        
        # Retry loop
        for attempt in range(self.max_retries + 1):
            try:
                # Record request time
                now = time.time()
                self.request_times[domain].append(now)
                self.last_request[domain] = now
                
                # Resolve hostname using DoTLS resolver
                parsed = urlparse(url)
                hostname = parsed.hostname
                request_headers = (headers.copy() if headers else {})
                original_hostname = hostname  # Store for TLS SNI
                use_custom_handler = False
                
                if hostname:
                    # Skip resolution if hostname is already an IP address
                    try:
                        ipaddress.ip_address(hostname)
                        # Already an IP, validate it
                        is_valid, error_msg = validate_ip_address(hostname)
                        if not is_valid:
                            raise ValueError(f'Invalid IP address {hostname}: {error_msg}')
                        # IP is valid, use as-is
                        resolved_ip = hostname
                    except ValueError:
                        # Not an IP, resolve using DoTLS
                        resolved_ip = resolve_hostname_dot(hostname)
                        if not resolved_ip:
                            raise ValueError(f'Failed to resolve {hostname} or resolved IP is invalid')
                        
                        # Replace hostname with resolved IP in URL
                        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
                        
                        # Reconstruct netloc with IP
                        if port:
                            if ':' in resolved_ip:
                                # IPv6, needs brackets
                                new_netloc = f'[{resolved_ip}]:{port}'
                            else:
                                new_netloc = f'{resolved_ip}:{port}'
                        else:
                            if ':' in resolved_ip:
                                # IPv6, needs brackets
                                new_netloc = f'[{resolved_ip}]'
                            else:
                                new_netloc = resolved_ip
                        
                        # Reconstruct URL with IP
                        url = parsed._replace(netloc=new_netloc).geturl()
                        # Set Host header to original hostname
                        request_headers['Host'] = hostname
                        # Use custom handler for HTTPS to set TLS hostname
                        if parsed.scheme == 'https':
                            use_custom_handler = True
                
                # Create opener with custom HTTPS handler if needed
                if use_custom_handler:
                    opener = urllib.request.build_opener(CustomHTTPSHandler(tls_hostname=original_hostname))
                else:
                    opener = urllib.request.build_opener()
                
                req = urllib.request.Request(url, headers=request_headers)
                with opener.open(req, timeout=timeout) as response:
                    # Reset retry count on success
                    self.retry_counts[url] = 0
                    
                    # Check content length if available
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > self.max_size:
                        self.logger.warning(
                            f'Response too large: {content_length} bytes (max: {self.max_size})'
                        )
                        return None
                    
                    # Read with size limit
                    data = response.read(self.max_size + 1)
                    if len(data) > self.max_size:
                        self.logger.warning(
                            f'Response exceeded max size: {len(data)} bytes (max: {self.max_size})'
                        )
                        return None
                    
                    # Try to parse as JSON
                    try:
                        return json.loads(data.decode('utf-8'))
                    except json.JSONDecodeError:
                        # Return raw text if not JSON
                        return {'text': data.decode('utf-8', errors='ignore')}
                        
            except urllib.error.HTTPError as e:
                self.retry_counts[url] = attempt + 1
                
                if self._should_retry(url, e) and attempt < self.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    self.logger.warning(
                        f'HTTP error {e.code} for {url}, retrying in {backoff:.2f}s (attempt {attempt + 1}/{self.max_retries})'
                    )
                    time.sleep(backoff)
                    continue
                else:
                    self.logger.error(f'HTTP error {e.code} for {url}: {e.reason}')
                    return None
                    
            except urllib.error.URLError as e:
                self.retry_counts[url] = attempt + 1
                
                if self._should_retry(url, e) and attempt < self.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    self.logger.warning(
                        f'URL error for {url}, retrying in {backoff:.2f}s (attempt {attempt + 1}/{self.max_retries}): {e.reason}'
                    )
                    time.sleep(backoff)
                    continue
                else:
                    self.logger.error(f'URL error for {url}: {e.reason}')
                    return None
                    
            except Exception as e:
                self.retry_counts[url] = attempt + 1
                
                if attempt < self.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    self.logger.warning(
                        f'Unexpected error for {url}, retrying in {backoff:.2f}s (attempt {attempt + 1}/{self.max_retries})'
                    )
                    self.logger.exception('Error details', e)
                    time.sleep(backoff)
                    continue
                else:
                    self.logger.exception('Unexpected error fetching URL', e)
                    return None
        
        return None
    
    def get_text(self, url: str, headers: Optional[Dict[str, str]] = None,
                 timeout: int = 10) -> Optional[str]:
        """Make a GET request and return text response."""
        result = self.get(url, headers, timeout)
        if result and isinstance(result, dict) and 'text' in result:
            return result['text']
        return None
    
    def post(self, url: str, data: Optional[bytes] = None,
             headers: Optional[Dict[str, str]] = None,
             timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Make a POST request with rate limiting, cooldown, and retry logic.
        Returns JSON response or None on error.
        """
        domain = self._get_domain(url)
        
        # Check rate limit
        if not self._check_rate_limit(domain):
            self.logger.warning(f'Rate limit exceeded for {domain}, request denied')
            return None
        
        # Wait for cooldown
        self._wait_cooldown(domain)
        
        # Retry loop
        for attempt in range(self.max_retries + 1):
            try:
                # Record request time
                now = time.time()
                self.request_times[domain].append(now)
                self.last_request[domain] = now
                
                # Resolve hostname using DoTLS resolver
                parsed = urlparse(url)
                hostname = parsed.hostname
                request_headers = (headers.copy() if headers else {})
                original_hostname = hostname  # Store for TLS SNI
                use_custom_handler = False
                
                if hostname:
                    # Skip resolution if hostname is already an IP address
                    try:
                        ipaddress.ip_address(hostname)
                        # Already an IP, validate it
                        is_valid, error_msg = validate_ip_address(hostname)
                        if not is_valid:
                            raise ValueError(f'Invalid IP address {hostname}: {error_msg}')
                        # IP is valid, use as-is
                        resolved_ip = hostname
                    except ValueError:
                        # Not an IP, resolve using DoTLS
                        resolved_ip = resolve_hostname_dot(hostname)
                        if not resolved_ip:
                            raise ValueError(f'Failed to resolve {hostname} or resolved IP is invalid')
                        
                        # Replace hostname with resolved IP in URL
                        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
                        
                        # Reconstruct netloc with IP
                        if port:
                            if ':' in resolved_ip:
                                # IPv6, needs brackets
                                new_netloc = f'[{resolved_ip}]:{port}'
                            else:
                                new_netloc = f'{resolved_ip}:{port}'
                        else:
                            if ':' in resolved_ip:
                                # IPv6, needs brackets
                                new_netloc = f'[{resolved_ip}]'
                            else:
                                new_netloc = resolved_ip
                        
                        # Reconstruct URL with IP
                        url = parsed._replace(netloc=new_netloc).geturl()
                        # Set Host header to original hostname
                        request_headers['Host'] = hostname
                        # Use custom handler for HTTPS to set TLS hostname
                        if parsed.scheme == 'https':
                            use_custom_handler = True
                
                # Create opener with custom HTTPS handler if needed
                if use_custom_handler:
                    opener = urllib.request.build_opener(CustomHTTPSHandler(tls_hostname=original_hostname))
                else:
                    opener = urllib.request.build_opener()
                
                req = urllib.request.Request(url, data=data, headers=request_headers)
                with opener.open(req, timeout=timeout) as response:
                    # Reset retry count on success
                    self.retry_counts[url] = 0
                    
                    # Check content length if available
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > self.max_size:
                        self.logger.warning(
                            f'Response too large: {content_length} bytes (max: {self.max_size})'
                        )
                        return None
                    
                    # Read with size limit
                    response_data = response.read(self.max_size + 1)
                    if len(response_data) > self.max_size:
                        self.logger.warning(
                            f'Response exceeded max size: {len(response_data)} bytes (max: {self.max_size})'
                        )
                        return None
                    
                    # Try to parse as JSON
                    try:
                        return json.loads(response_data.decode('utf-8'))
                    except json.JSONDecodeError:
                        # Return raw text if not JSON
                        return {'text': response_data.decode('utf-8', errors='ignore')}
                        
            except urllib.error.HTTPError as e:
                self.retry_counts[url] = attempt + 1
                
                if self._should_retry(url, e) and attempt < self.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    self.logger.warning(
                        f'HTTP error {e.code} for {url}, retrying in {backoff:.2f}s (attempt {attempt + 1}/{self.max_retries})'
                    )
                    time.sleep(backoff)
                    continue
                else:
                    self.logger.error(f'HTTP error {e.code} for {url}: {e.reason}')
                    return None
                    
            except urllib.error.URLError as e:
                self.retry_counts[url] = attempt + 1
                
                if self._should_retry(url, e) and attempt < self.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    self.logger.warning(
                        f'URL error for {url}, retrying in {backoff:.2f}s (attempt {attempt + 1}/{self.max_retries}): {e.reason}'
                    )
                    time.sleep(backoff)
                    continue
                else:
                    self.logger.error(f'URL error for {url}: {e.reason}')
                    return None
                    
            except Exception as e:
                self.retry_counts[url] = attempt + 1
                
                if attempt < self.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    self.logger.warning(
                        f'Unexpected error for {url}, retrying in {backoff:.2f}s (attempt {attempt + 1}/{self.max_retries})'
                    )
                    self.logger.exception('Error details', e)
                    time.sleep(backoff)
                    continue
                else:
                    self.logger.exception('Unexpected error fetching URL', e)
                    return None
        
        return None


# Text formatting utility
class IRCFormatter:
    """IRC text formatting utilities (no colors)."""
    
    @staticmethod
    def bold(text: str) -> str:
        """Make text bold."""
        return f'\x02{text}\x02'
    
    @staticmethod
    def italic(text: str) -> str:
        """Make text italic."""
        return f'\x1d{text}\x1d'
    
    @staticmethod
    def underline(text: str) -> str:
        """Underline text."""
        return f'\x1f{text}\x1f'
    
    @staticmethod
    def strikethrough(text: str) -> str:
        """Strikethrough text."""
        return f'\x1e{text}\x1e'
    
    @staticmethod
    def monospace(text: str) -> str:
        """Monospace text."""
        return f'\x11{text}\x11'
    
    @staticmethod
    def reverse(text: str) -> str:
        """Reverse video (swap foreground/background)."""
        return f'\x16{text}\x16'
    
    @staticmethod
    def table(data: List[List[str]], headers: Optional[List[str]] = None,
              max_width: int = 400) -> str:
        """
        Format data as a table.
        Returns formatted string suitable for IRC.
        """
        if not data:
            return 'No data'
        
        # Include headers if provided
        if headers:
            rows = [headers] + data
        else:
            rows = data
        
        # Calculate column widths
        num_cols = len(rows[0])
        col_widths = [0] * num_cols
        
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Limit column widths to prevent overflow
        total_width = sum(col_widths) + (num_cols - 1) * 3  # 3 for separators
        if total_width > max_width:
            scale = max_width / total_width
            col_widths = [int(w * scale) for w in col_widths]
        
        # Format rows
        lines = []
        for i, row in enumerate(rows):
            formatted_row = ' | '.join(
                str(cell)[:col_widths[j]].ljust(col_widths[j])
                for j, cell in enumerate(row)
            )
            lines.append(formatted_row)
            
            # Add separator after headers
            if headers and i == 0:
                lines.append('-+-'.join('-' * w for w in col_widths))
        
        return '\n'.join(lines)
    
    @staticmethod
    def truncate(text: str, max_len: int = 300, suffix: str = '...') -> str:
        """Truncate text to max length."""
        if len(text) <= max_len:
            return text
        return text[:max_len - len(suffix)] + suffix
    
    @staticmethod
    def bar_chart(data: Dict[str, float], width: int = 40, height: int = 8,
                  max_value: Optional[float] = None, 
                  show_values: bool = False) -> str:
        """
        Create a vertical bar chart from data.
        
        Args:
            data: Dictionary of label -> value pairs
            width: Maximum width of chart in characters
            height: Height of chart in lines
            max_value: Maximum value for scaling (auto if None)
            show_values: Whether to show numeric values
        
        Returns:
            Formatted bar chart as string
        """
        if not data:
            return 'No data'
        
        # Unicode block elements for bars (8 levels)
        blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        
        # Calculate max value if not provided
        if max_value is None:
            max_value = max(data.values()) if data.values() else 1
        
        if max_value == 0:
            max_value = 1
        
        # Calculate bar width per item
        num_items = len(data)
        bar_width = max(1, width // (num_items * 2))  # Leave space between bars
        
        lines = []
        
        # Draw from top to bottom
        for y in range(height - 1, -1, -1):
            line_parts = []
            threshold = (y + 1) / height * max_value
            
            for label, value in data.items():
                # Determine block level
                level = int((value / max_value) * height * 8) if max_value > 0 else 0
                level = max(0, min(8, level))
                
                # Draw bar
                if value >= threshold:
                    block = blocks[8]  # Full block
                elif value >= threshold - (max_value / height / 8):
                    block = blocks[level % 9]
                else:
                    block = blocks[0]  # Space
                
                # Build bar
                bar = block * bar_width
                line_parts.append(bar)
            
            lines.append(''.join(line_parts))
        
        # Add labels and values
        label_line = ''
        value_line = ''
        
        for label, value in data.items():
            label_short = label[:bar_width]
            label_line += label_short.ljust(bar_width)
            
            if show_values:
                value_str = f'{value:.1f}'[:bar_width]
                value_line += value_str.ljust(bar_width)
        
        result_lines = lines + [label_line]
        if show_values:
            result_lines.append(value_line)
        
        return '\n'.join(result_lines)
    
    @staticmethod
    def horizontal_bar(values: List[float], labels: Optional[List[str]] = None,
                      width: int = 40, show_values: bool = True,
                      fill_char: str = '█', empty_char: str = '░') -> str:
        """
        Create horizontal bar chart from values.
        
        Args:
            values: List of numeric values
            labels: Optional list of labels (one per value)
            width: Maximum width of bars in characters
            show_values: Whether to show numeric values
            fill_char: Character to use for filled portion
            empty_char: Character to use for empty portion
        
        Returns:
            Formatted horizontal bar chart as string
        """
        if not values:
            return 'No data'
        
        max_value = max(abs(v) for v in values) if values else 1
        if max_value == 0:
            max_value = 1
        
        lines = []
        
        for i, value in enumerate(values):
            label = labels[i] if labels and i < len(labels) else f'Item {i+1}'
            
            # Calculate bar length
            bar_length = int((abs(value) / max_value) * width)
            bar_length = max(0, min(width, bar_length))
            
            # Build bar
            bar = fill_char * bar_length + empty_char * (width - bar_length)
            
            # Format line
            if show_values:
                line = f'{label:15} │{bar}│ {value:.2f}'
            else:
                line = f'{label:15} │{bar}│'
            
            lines.append(line)
        
        return '\n'.join(lines)
    
    @staticmethod
    def sparkline(values: List[float], width: int = 30, 
                  height: int = 3, show_bounds: bool = False) -> str:
        """
        Create a sparkline (mini line chart) from values.
        
        Args:
            values: List of numeric values
            width: Width of sparkline in characters
            height: Height of sparkline in lines
            show_bounds: Whether to show min/max values
        
        Returns:
            Formatted sparkline as string
        """
        if not values:
            return 'No data'
        
        if len(values) < 2:
            return str(values[0]) if values else 'No data'
        
        # Unicode block elements for different heights
        blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        
        # Normalize values to fit in width
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        if range_val == 0:
            range_val = 1
        
        # Sample values to fit width
        num_points = min(width, len(values))
        step = len(values) / num_points
        sampled = []
        
        for i in range(num_points):
            idx = int(i * step)
            if idx < len(values):
                sampled.append(values[idx])
        
        # Normalize to 0-8 range (8 block levels)
        normalized = [
            int(((v - min_val) / range_val) * (height * 8 - 1))
            for v in sampled
        ]
        
        # Create sparkline
        lines = []
        for y in range(height - 1, -1, -1):
            line = ''
            threshold_low = y * 8
            threshold_high = (y + 1) * 8
            
            for val in normalized:
                if val >= threshold_high:
                    block = blocks[8]  # Full block
                elif val >= threshold_low:
                    level = (val - threshold_low) % 9
                    block = blocks[level]
                else:
                    block = blocks[0]  # Space
                
                line += block
            
            lines.append(line)
        
        result = '\n'.join(lines)
        
        if show_bounds:
            result += f'\nMin: {min_val:.2f} Max: {max_val:.2f}'
        
        return result
    
    @staticmethod
    def histogram(values: List[float], bins: int = 10, width: int = 40,
                  fill_char: str = '█') -> str:
        """
        Create a histogram from values.
        
        Args:
            values: List of numeric values
            bins: Number of bins for histogram
            width: Maximum width of histogram bars
            fill_char: Character to use for bars
        
        Returns:
            Formatted histogram as string
        """
        if not values:
            return 'No data'
        
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        
        if range_val == 0:
            # All values are the same
            bin_counts = [len(values)] + [0] * (bins - 1)
            bin_labels = [f'{min_val:.2f}']
        else:
            # Create bins
            bin_counts = [0] * bins
            bin_width = range_val / bins
            
            for value in values:
                bin_idx = min(int((value - min_val) / bin_width), bins - 1)
                bin_counts[bin_idx] += 1
            
            # Generate bin labels
            bin_labels = []
            for i in range(bins):
                bin_start = min_val + i * bin_width
                bin_end = min_val + (i + 1) * bin_width
                bin_labels.append(f'{bin_start:.1f}-{bin_end:.1f}')
        
        # Normalize counts for display
        max_count = max(bin_counts) if bin_counts else 1
        
        lines = []
        for i, count in enumerate(bin_counts):
            bar_length = int((count / max_count) * width)
            bar = fill_char * bar_length
            label = bin_labels[i] if i < len(bin_labels) else f'Bin {i+1}'
            lines.append(f'{label:15} │{bar}│ {count}')
        
        return '\n'.join(lines)
    
    @staticmethod
    def progress_bar(current: float, total: float, width: int = 30,
                    fill_char: str = '█', empty_char: str = '░',
                    show_percent: bool = True) -> str:
        """
        Create a progress bar.
        
        Args:
            current: Current value
            total: Total/maximum value
            width: Width of progress bar
            fill_char: Character for filled portion
            empty_char: Character for empty portion
            show_percent: Whether to show percentage
        
        Returns:
            Formatted progress bar as string
        """
        if total == 0:
            percent = 0.0
        else:
            percent = min(100.0, max(0.0, (current / total) * 100.0))
        
        filled = int((percent / 100.0) * width)
        filled = max(0, min(width, filled))
        empty = width - filled
        
        bar = fill_char * filled + empty_char * empty
        
        if show_percent:
            return f'[{bar}] {percent:.1f}%'
        else:
            return f'[{bar}]'
    
    @staticmethod
    def candlestick(candles: List[Dict[str, float]], width: int = 60, height: int = 15,
                   labels: Optional[List[str]] = None, 
                   bullish_char: str = '█', bearish_char: str = '█',
                   wick_char: str = '│') -> str:
        """
        Create a candlestick chart from OHLC data.
        
        Args:
            candles: List of dictionaries with 'open', 'high', 'low', 'close' keys
            width: Width of chart in characters
            height: Height of chart in lines
            labels: Optional list of labels for each candle
            bullish_char: Character for bullish (green/up) candles
            bearish_char: Character for bearish (red/down) candles
            wick_char: Character for wicks (high/low lines)
        
        Returns:
            Formatted candlestick chart as string
        """
        if not candles:
            return 'No data'
        
        # Extract OHLC values
        ohlc_data = []
        for candle in candles:
            ohlc = {
                'open': candle.get('open', 0),
                'high': candle.get('high', 0),
                'low': candle.get('low', 0),
                'close': candle.get('close', 0)
            }
            ohlc_data.append(ohlc)
        
        # Find min/max for scaling
        all_highs = [ohlc['high'] for ohlc in ohlc_data]
        all_lows = [ohlc['low'] for ohlc in ohlc_data]
        min_price = min(all_lows) if all_lows else 0
        max_price = max(all_highs) if all_highs else 1
        
        price_range = max_price - min_price
        if price_range == 0:
            price_range = 1
        
        # Calculate candle width
        num_candles = len(ohlc_data)
        candle_width = max(1, width // num_candles - 1)  # Leave space between candles
        candle_width = min(candle_width, 5)  # Limit max width for readability
        
        # Create grid for plotting
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Plot each candle
        for i, ohlc in enumerate(ohlc_data):
            open_price = ohlc['open']
            high_price = ohlc['high']
            low_price = ohlc['low']
            close_price = ohlc['close']
            
            # Determine if bullish (close > open) or bearish (close <= open)
            is_bullish = close_price >= open_price
            body_top = max(open_price, close_price)
            body_bottom = min(open_price, close_price)
            body_char = bullish_char if is_bullish else bearish_char
            
            # Calculate positions in grid (y is inverted - 0 is top, height-1 is bottom)
            def price_to_y(price: float) -> int:
                normalized = (price - min_price) / price_range
                y = int((1.0 - normalized) * (height - 1))
                return max(0, min(height - 1, y))
            
            high_y = price_to_y(high_price)
            low_y = price_to_y(low_price)
            body_top_y = price_to_y(body_top)
            body_bottom_y = price_to_y(body_bottom)
            
            # Calculate x position (centered in candle's space)
            x_start = i * (candle_width + 1)
            x_center = x_start + candle_width // 2
            
            # Draw wick (high-low line)
            for y in range(low_y, high_y + 1):
                if 0 <= x_center < width:
                    grid[y][x_center] = wick_char
            
            # Draw body (open-close rectangle)
            if body_top_y == body_bottom_y:
                # Single line body
                for x in range(x_start, min(x_start + candle_width, width)):
                    if 0 <= body_top_y < height:
                        grid[body_top_y][x] = body_char
            else:
                # Multi-line body
                for y in range(body_bottom_y, body_top_y + 1):
                    for x in range(x_start, min(x_start + candle_width, width)):
                        if 0 <= y < height and 0 <= x < width:
                            grid[y][x] = body_char
            
            # Overlay wick on body (ensure wick is visible)
            if 0 <= x_center < width:
                for y in range(low_y, high_y + 1):
                    grid[y][x_center] = wick_char
        
        # Convert grid to string lines
        lines = []
        for row in grid:
            lines.append(''.join(row))
        
        # Add price scale on the right
        scale_lines = []
        for i, line in enumerate(lines):
            y_ratio = i / (height - 1) if height > 1 else 0
            price = max_price - (price_range * y_ratio)
            scale_lines.append(f'{line} │ {price:.2f}')
        
        result = '\n'.join(scale_lines)
        
        # Add labels if provided
        if labels:
            label_line = ' ' * width + '│ '
            for i, label in enumerate(labels[:num_candles]):
                x_pos = i * (candle_width + 1) + candle_width // 2
                if x_pos < width:
                    label_short = label[:candle_width]
                    # Try to center label under candle
                    start_pos = max(0, x_pos - len(label_short) // 2)
                    label_line = label_line[:start_pos] + label_short + label_line[start_pos + len(label_short):]
                    label_line = label_line[:width] + '│ ' + label_line[width:]
            result += '\n' + label_line[:width + 20]  # Limit label line length
        
        return result
    
    @staticmethod
    def candlestick_simple(open_price: float, high_price: float, low_price: float, 
                          close_price: float, width: int = 20) -> str:
        """
        Create a single simple candlestick representation.
        
        Args:
            open_price: Opening price
            high_price: High price
            low_price: Low price
            close_price: Closing price
            width: Width of display
        
        Returns:
            Simple candlestick string representation
        """
        is_bullish = close_price >= open_price
        
        # Determine price range
        price_range = high_price - low_price
        if price_range == 0:
            price_range = 1
        
        # Normalize positions (0-1 scale)
        high_pos = 1.0
        low_pos = 0.0
        open_pos = (open_price - low_price) / price_range
        close_pos = (close_price - low_price) / price_range
        
        body_top = max(open_pos, close_pos)
        body_bottom = min(open_pos, close_pos)
        
        # Create simple visualization
        height = 10
        chart = [' ' * width for _ in range(height)]
        
        # Draw wick
        wick_x = width // 2
        for y in range(height):
            chart[y] = chart[y][:wick_x] + '│' + chart[y][wick_x + 1:]
        
        # Draw body
        body_start = max(0, int(width * 0.3))
        body_end = min(width, int(width * 0.7))
        body_width = body_end - body_start
        
        body_top_y = int((1.0 - body_top) * (height - 1))
        body_bottom_y = int((1.0 - body_bottom) * (height - 1))
        
        body_char = '█' if is_bullish else '░'
        
        for y in range(body_bottom_y, body_top_y + 1):
            for x in range(body_start, body_end):
                if 0 <= x < width and 0 <= y < height:
                    chart[y] = chart[y][:x] + body_char + chart[y][x + 1:]
        
        # Build result
        lines = []
        for row in chart:
            lines.append(row)
        
        # Add price info
        price_info = f'O:{open_price:.2f} H:{high_price:.2f} L:{low_price:.2f} C:{close_price:.2f}'
        if is_bullish:
            price_info += ' ▲'
        else:
            price_info += ' ▼'
        
        lines.append(price_info)
        
        return '\n'.join(lines)


# Permissions utility
class Permissions:
    """Helper for Sopel permission checks."""
    
    @staticmethod
    def require_privilege(bot, trigger, level: int):
        """
        Require a privilege level.
        Levels: 0=anyone, 1=voiced, 2=halfop, 3=op, 4=admin, 5=owner
        """
        if not trigger.sender:
            return False
        
        if level == 0:
            return True
        
        channel = trigger.sender
        nick = trigger.nick
        
        if level >= 5:  # Owner
            if bot.config.core.owner and nick.lower() == bot.config.core.owner.lower():
                return True
        
        if level >= 4:  # Admin
            if bot.config.core.admins and nick.lower() in [a.lower() for a in bot.config.core.admins]:
                return True
        
        if level >= 3:  # Op
            if bot.channels[channel].privileges[nick] >= plugin.OP:
                return True
        
        if level >= 2:  # Halfop
            if bot.channels[channel].privileges[nick] >= plugin.HALFOP:
                return True
        
        if level >= 1:  # Voiced
            if bot.channels[channel].privileges[nick] >= plugin.VOICE:
                return True
        
        return False
    
    @staticmethod
    def has_privilege(bot, trigger, level: int) -> bool:
        """Check if user has privilege level."""
        return Permissions.require_privilege(bot, trigger, level)


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
            logger.error(f'XML parse error: {e}')
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


# GraphQL client utility
class GraphQLClient:
    """GraphQL client using gql library with sync transport."""
    
    def __init__(self, endpoint: str, headers: Optional[Dict[str, str]] = None):
        """Initialize GraphQL client with endpoint and optional headers."""
        self.endpoint = endpoint
        self.headers = headers or {}
        self.logger = get_logger('graphql_client')
        self._client = None
    
    def _get_client(self):
        """Get or create GraphQL client."""
        if self._client is None:
            try:
                from gql import Client, gql
                from gql.transport.requests import RequestsHTTPTransport
                
                transport = RequestsHTTPTransport(
                    url=self.endpoint,
                    headers=self.headers,
                    use_json=True
                )
                
                self._client = Client(transport=transport, fetch_schema_from_transport=False)
            except ImportError:
                self.logger.error('gql library not available. Install with: pip install gql requests')
                return None
            except Exception as e:
                self.logger.exception('Error creating GraphQL client', e)
                return None
        return self._client
    
    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a GraphQL query.
        Returns JSON response or None on error.
        """
        try:
            from gql import gql
            
            client = self._get_client()
            if client is None:
                return None
            
            gql_query = gql(query)
            result = client.execute(gql_query, variable_values=variables or {})
            
            return result
            
        except Exception as e:
            self.logger.exception('Error executing GraphQL query', e)
            return None


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
                elif prop == 'og:video':
                    videos.append(content)
                elif prop == 'og:video:url':
                    videos.append(content)
                elif prop == 'og:audio':
                    audios.append(content)
                elif prop == 'og:audio:url':
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

