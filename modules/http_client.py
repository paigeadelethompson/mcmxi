"""
HTTP client utilities with rate limiting, retry logic, and DNS resolver.
Always uses DNS module for resolution and supports proxy configuration.
"""
import http.client
import ipaddress
import json
import os
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from typing import Any, Dict, Optional
from urllib.parse import quote, urlparse

from sopel.tools import get_logger

# Import DNS resolution functions from DNS module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dns_module import resolve_hostname_dot


def _validate_resolved_ip(ip: str) -> None:
    """Validate that resolved IP is not private, reserved, multicast, etc. Raises ValueError if invalid."""
    try:
        addr = ipaddress.ip_address(ip)
        if addr.is_multicast:
            raise ValueError(f'IP {ip} is multicast address')
        if addr.is_reserved:
            raise ValueError(f'IP {ip} is reserved address')
        if addr.is_private:
            raise ValueError(f'IP {ip} is private address')
        if addr.is_loopback:
            raise ValueError(f'IP {ip} is loopback address')
        if addr.is_link_local:
            raise ValueError(f'IP {ip} is link-local address')
    except ValueError:
        raise  # Re-raise if it's our validation error
    except Exception as e:
        raise ValueError(f'Invalid IP address {ip}: {e}')


class CustomHTTPSHandler(urllib.request.HTTPSHandler):
    """HTTPS handler that uses DNS resolver and sets TLS hostname (SNI)."""

    def __init__(self, tls_hostname=None):
        self.tls_hostname = tls_hostname
        self.logger = get_logger('http_client')
        context = ssl.create_default_context()
        super().__init__(context=context)

    def https_open(self, req):
        """Open HTTPS connection with custom TLS hostname."""
        return self.do_open(self._make_connection, req)

    def _make_connection(self, host, port=443, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, **kwargs):
        """Create HTTPS connection using DNS resolver."""
        # Extract hostname from host (may include port)
        host_clean = host.replace('[', '').replace(']', '')
        if ':' in host_clean:
            parts = host_clean.rsplit(':', 1)
            if len(parts) == 2:
                host_clean = parts[0]
        
        # Resolve hostname using DNS module
        try:
            ipaddress.ip_address(host_clean)
            # Already an IP - validate it
            resolved_ip = host_clean
            _validate_resolved_ip(resolved_ip)
        except ValueError as e:
            if 'is multicast' in str(e) or 'is reserved' in str(e) or 'is private' in str(e) or 'is loopback' in str(e) or 'is link-local' in str(e) or 'Invalid IP address' in str(e):
                raise
            # Not an IP, resolve using DNS module
            self.logger.info(f'Resolving {host_clean} using DNS module')
            resolved_ip = resolve_hostname_dot(host_clean)
            if not resolved_ip:
                raise ValueError(f'Failed to resolve {host_clean} using DNS module')
            # Validate resolved IP
            _validate_resolved_ip(resolved_ip)
            self.logger.info(f'Resolved {host_clean} to {resolved_ip}')
        
        self.logger.info(f'Connecting to {resolved_ip}:{port} (hostname: {self.tls_hostname})')
        sock = socket.create_connection((resolved_ip, port), timeout)
        context = self._context
        if self.tls_hostname:
            ssock = context.wrap_socket(sock, server_hostname=self.tls_hostname)
        else:
            ssock = context.wrap_socket(sock)
        conn = http.client.HTTPSConnection(host, port=port, timeout=timeout)
        conn.sock = ssock
        return conn


class CustomHTTPHandler(urllib.request.HTTPHandler):
    """HTTP handler that uses DNS resolver."""

    def __init__(self):
        self.logger = get_logger('http_client')
        super().__init__()

    def http_open(self, req):
        """Open HTTP connection using DNS resolver."""
        return self.do_open(self._make_connection, req)

    def _make_connection(self, host, port=80, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, **kwargs):
        """Create HTTP connection using DNS resolver."""
        # Extract hostname from host (may include port)
        host_clean = host.replace('[', '').replace(']', '')
        if ':' in host_clean:
            parts = host_clean.rsplit(':', 1)
            if len(parts) == 2:
                host_clean = parts[0]
        
        # Resolve hostname using DNS module
        try:
            ipaddress.ip_address(host_clean)
            # Already an IP - validate it
            resolved_ip = host_clean
            _validate_resolved_ip(resolved_ip)
        except ValueError as e:
            if 'is multicast' in str(e) or 'is reserved' in str(e) or 'is private' in str(e) or 'is loopback' in str(e) or 'is link-local' in str(e) or 'Invalid IP address' in str(e):
                raise
            # Not an IP, resolve using DNS module
            self.logger.info(f'Resolving {host_clean} using DNS module')
            resolved_ip = resolve_hostname_dot(host_clean)
            if not resolved_ip:
                raise ValueError(f'Failed to resolve {host_clean} using DNS module')
            # Validate resolved IP
            _validate_resolved_ip(resolved_ip)
            self.logger.info(f'Resolved {host_clean} to {resolved_ip}')
        
        self.logger.info(f'Connecting to {resolved_ip}:{port}')
        sock = socket.create_connection((resolved_ip, port), timeout)
        conn = http.client.HTTPConnection(host, port=port, timeout=timeout)
        conn.sock = sock
        return conn


class HTTPClient:
    """HTTP client with rate limiting, retry logic, and DNS resolver."""

    def __init__(self, max_size: int = 5 * 1024 * 1024, max_retries: int = 3):
        self.max_size = max_size
        self.max_retries = max_retries
        self.logger = get_logger('http_client')
        self.request_times = defaultdict(list)
        self.last_request = {}
        self.retry_counts = defaultdict(int)
        self.cooldown_period = 1.0
        self.rate_limit = 10  # requests per minute per domain

    @staticmethod
    def quote(string: str, safe: str = '/') -> str:
        """URL-encode a string. Wrapper around urllib.parse.quote."""
        return quote(string, safe=safe)

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc or url

    def _check_rate_limit(self, domain: str) -> bool:
        """Check if rate limit is exceeded."""
        now = time.time()
        # Remove requests older than 1 minute
        self.request_times[domain] = [
            t for t in self.request_times[domain] if now - t < 60
        ]
        return len(self.request_times[domain]) < self.rate_limit

    def _wait_cooldown(self, domain: str):
        """Wait for cooldown period if needed."""
        if domain in self.last_request:
            elapsed = time.time() - self.last_request[domain]
            if elapsed < self.cooldown_period:
                time.sleep(self.cooldown_period - elapsed)

    def _should_retry(self, url: str, error: Exception) -> bool:
        """Determine if request should be retried."""
        if isinstance(error, urllib.error.HTTPError):
            # Retry on 5xx errors
            return 500 <= error.code < 600
        elif isinstance(error, urllib.error.URLError):
            # Retry on network errors
            return True
        return False

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        return min(2 ** attempt, 10.0)

    def _resolve_hostname(self, hostname: str) -> str:
        """Resolve hostname to IP using DNS module."""
        # Check if already an IP
        try:
            ipaddress.ip_address(hostname)
            # Validate IP
            _validate_resolved_ip(hostname)
            return hostname
        except ValueError:
            pass  # Not an IP, continue to DNS resolution
        
        # MUST use DNS module to resolve
        self.logger.info(f'Resolving {hostname} using DNS module')
        start_time = time.time()
        resolved_ip = resolve_hostname_dot(hostname)
        elapsed = time.time() - start_time
        if not resolved_ip:
            self.logger.error(f'DNS resolution failed for {hostname} after {elapsed:.2f}s')
            raise ValueError(f'Failed to resolve {hostname} using DNS module')
        
        # Validate resolved IP
        _validate_resolved_ip(resolved_ip)
        
        self.logger.info(f'DNS module resolved {hostname} to {resolved_ip} in {elapsed:.2f}s')
        return resolved_ip

    def _prepare_request(self, url: str, headers: Dict[str, str]) -> tuple:
        """Resolve DNS and prepare request. Returns (url, original_hostname, is_https)."""
        parsed = urlparse(url)
        hostname = parsed.hostname
        original_hostname = hostname

        if not hostname:
            return url, original_hostname, False

        # Resolve DNS using DNS module
        resolved_ip = self._resolve_hostname(hostname)
        
        # When using proxy, keep original hostname in URL (proxy needs it)
        # When not using proxy, replace with IP to bypass system DNS
        has_proxy = bool(os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY'))
        
        is_https = parsed.scheme == 'https'
        
        if not has_proxy:
            # No proxy: replace hostname with IP
            port = parsed.port or (443 if is_https else 80)
            if port:
                if ':' in resolved_ip:
                    new_netloc = f'[{resolved_ip}]:{port}'
                else:
                    new_netloc = f'{resolved_ip}:{port}'
            elif ':' in resolved_ip:
                new_netloc = f'[{resolved_ip}]'
            else:
                new_netloc = resolved_ip
            url = parsed._replace(netloc=new_netloc).geturl()
            self.logger.debug(f'Replaced hostname with IP: {hostname} -> {resolved_ip}')
        else:
            # Proxy configured: keep hostname
            self.logger.debug(f'Proxy configured, keeping hostname: {hostname}')
        
        headers['Host'] = hostname
        return url, original_hostname, is_https

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Make a GET request with rate limiting, cooldown, and retry logic."""
        domain = self._get_domain(url)

        if not self._check_rate_limit(domain):
            return None

        self._wait_cooldown(domain)

        for attempt in range(self.max_retries + 1):
            try:
                now = time.time()
                self.request_times[domain].append(now)
                self.last_request[domain] = now

                request_headers = (headers.copy() if headers else {})
                
                # Check if proxy is configured
                https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
                http_proxy = os.environ.get('HTTP_PROXY')
                has_proxy = bool(https_proxy or http_proxy)
                
                if has_proxy:
                    # Proxy configured: resolve DNS for verification, keep hostname in URL
                    parsed = urlparse(url)
                    hostname = parsed.hostname
                    if hostname:
                        try:
                            resolved_ip = self._resolve_hostname(hostname)
                            self.logger.debug(f'DNS resolved {hostname} to {resolved_ip} (proxy will handle connection)')
                        except ValueError as e:
                            self.logger.error(f'DNS resolution failed for {url}: {e}')
                            return None
                    final_url = url  # Keep original URL with hostname for proxy CONNECT
                    is_https = parsed.scheme == 'https'
                else:
                    # No proxy: resolve DNS and replace hostname with IP
                    try:
                        final_url, original_hostname, is_https = self._prepare_request(url, request_headers)
                    except ValueError as e:
                        self.logger.error(f'DNS resolution failed for {url}: {e}')
                        return None

                # Configure handlers
                handlers = []
                if has_proxy:
                    # Proxy configured: use ProxyHandler and standard handlers
                    proxies = {}
                    if http_proxy:
                        proxies['http'] = http_proxy
                    if https_proxy:
                        proxies['https'] = https_proxy
                    handlers.append(urllib.request.ProxyHandler(proxies))
                    # Use standard handlers - ProxyHandler handles CONNECT
                    if is_https:
                        handlers.append(urllib.request.HTTPSHandler())
                    else:
                        handlers.append(urllib.request.HTTPHandler())
                else:
                    # No proxy: use custom handlers that resolve DNS
                    if is_https:
                        handlers.append(CustomHTTPSHandler(tls_hostname=original_hostname))
                    else:
                        handlers.append(CustomHTTPHandler())
                
                opener = urllib.request.build_opener(*handlers)

                req = urllib.request.Request(final_url, headers=request_headers)
                with opener.open(req, timeout=timeout) as response:
                    self.retry_counts[url] = 0

                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > self.max_size:
                        return None

                    data = response.read(self.max_size + 1)
                    if len(data) > self.max_size:
                        return None

                    try:
                        return json.loads(data.decode('utf-8'))
                    except json.JSONDecodeError:
                        return {'text': data.decode('utf-8', errors='ignore')}

            except urllib.error.HTTPError as e:
                self.retry_counts[url] = attempt + 1
                if self._should_retry(url, e) and attempt < self.max_retries:
                    time.sleep(self._calculate_backoff(attempt))
                    continue
                return None

            except urllib.error.URLError as e:
                self.retry_counts[url] = attempt + 1
                if self._should_retry(url, e) and attempt < self.max_retries:
                    time.sleep(self._calculate_backoff(attempt))
                    continue
                return None

            except Exception as e:
                self.logger.error(f'Unexpected error for {url}: {e}')
                self.logger.exception(e)
                return None

        return None

    def post(self, url: str, data: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Make a POST request with rate limiting, cooldown, and retry logic."""
        domain = self._get_domain(url)

        if not self._check_rate_limit(domain):
            return None

        self._wait_cooldown(domain)

        for attempt in range(self.max_retries + 1):
            try:
                now = time.time()
                self.request_times[domain].append(now)
                self.last_request[domain] = now

                request_headers = (headers.copy() if headers else {})
                try:
                    final_url, original_hostname, is_https = self._prepare_request(url, request_headers)
                except ValueError as e:
                    self.logger.error(f'DNS resolution failed for {url}: {e}')
                    return None

                # Configure proxy from environment
                handlers = []
                https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
                http_proxy = os.environ.get('HTTP_PROXY')
                if https_proxy or http_proxy:
                    proxies = {}
                    if http_proxy:
                        proxies['http'] = http_proxy
                    if https_proxy:
                        proxies['https'] = https_proxy
                    handlers.append(urllib.request.ProxyHandler(proxies))
                
                # Use custom handlers that use DNS resolver
                if is_https:
                    handlers.append(CustomHTTPSHandler(tls_hostname=original_hostname))
                else:
                    handlers.append(CustomHTTPHandler())
                
                opener = urllib.request.build_opener(*handlers)

                req = urllib.request.Request(final_url, data=data, headers=request_headers)
                with opener.open(req, timeout=timeout) as response:
                    self.retry_counts[url] = 0

                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > self.max_size:
                        return None

                    response_data = response.read(self.max_size + 1)
                    if len(response_data) > self.max_size:
                        return None

                    try:
                        return json.loads(response_data.decode('utf-8'))
                    except json.JSONDecodeError:
                        return {'text': response_data.decode('utf-8', errors='ignore')}

            except urllib.error.HTTPError as e:
                self.retry_counts[url] = attempt + 1
                if self._should_retry(url, e) and attempt < self.max_retries:
                    time.sleep(self._calculate_backoff(attempt))
                    continue
                return None

            except urllib.error.URLError as e:
                self.retry_counts[url] = attempt + 1
                if self._should_retry(url, e) and attempt < self.max_retries:
                    time.sleep(self._calculate_backoff(attempt))
                    continue
                return None

            except Exception as e:
                self.logger.error(f'Unexpected error for {url}: {e}')
                self.logger.exception(e)
                return None

        return None

