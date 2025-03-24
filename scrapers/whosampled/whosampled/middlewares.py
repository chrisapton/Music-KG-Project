import random
import time
import cloudscraper
import logging
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.http import HtmlResponse


class RandomUserAgentMiddleware(UserAgentMiddleware):
    """Middleware to rotate User-Agents for each request"""

    def __init__(self, user_agent_list):
        self.user_agent_list = user_agent_list
        super(RandomUserAgentMiddleware, self).__init__()

    @classmethod
    def from_crawler(cls, crawler):
        # Load user agents from settings
        user_agent_list = crawler.settings.get('USER_AGENT_LIST', [])
        if not user_agent_list:
            user_agent_list = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.0.0 Safari/537.36',
            ]

        middleware = cls(user_agent_list)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = user_agent
        spider.logger.debug(f"Using User-Agent: {user_agent}")


class RequestHeadersMiddleware:
    """Middleware to add realistic browser headers to each request"""

    def __init__(self):
        self.default_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

    def process_request(self, request, spider):
        # Add default headers to each request
        for key, value in self.default_headers.items():
            if key not in request.headers:
                request.headers[key] = value

        # Add referer for non-initial requests
        if 'Referer' not in request.headers and request.meta.get('depth', 0) > 0:
            request.headers['Referer'] = 'https://www.whosampled.com/'


class ProxyMiddleware:
    """Middleware to rotate proxies for each request"""

    def __init__(self, proxy_list):
        self.proxy_list = proxy_list
        self.current_proxy = None

    @classmethod
    def from_crawler(cls, crawler):
        # Load proxies from settings
        proxy_list = crawler.settings.get('PROXY_LIST', [])
        return cls(proxy_list)

    def process_request(self, request, spider):
        if not self.proxy_list:
            return

        # Select a proxy
        proxy = random.choice(self.proxy_list)
        self.current_proxy = proxy

        # Set the proxy for the request
        request.meta['proxy'] = proxy
        spider.logger.debug(f"Using proxy: {proxy}")


class RandomDelayMiddleware:
    """Middleware to add random delays between requests"""

    def __init__(self, delay):
        self.delay = delay

    @classmethod
    def from_crawler(cls, crawler):
        delay = crawler.settings.get('RANDOM_DELAY', [5, 10])
        return cls(delay)

    def process_request(self, request, spider):
        if isinstance(self.delay, list) and len(self.delay) == 2:
            min_delay, max_delay = self.delay
            delay = random.uniform(min_delay, max_delay)
        else:
            delay = self.delay

        spider.logger.debug(f"Sleeping for {delay} seconds")
        time.sleep(delay)


class CloudflareMiddleware:
    """
    Middleware to bypass Cloudflare protection with fixed content encoding handling
    """

    def __init__(self, browser_type=None):
        # Create a cloudscraper instance with optional browser emulation
        if browser_type:
            self.scraper = cloudscraper.create_scraper(browser={
                'browser': browser_type,
                'platform': 'linux',
                'mobile': False
            })
        else:
            self.scraper = cloudscraper.create_scraper()

        # Setup logging
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        # Get browser type from settings if available
        browser_type = crawler.settings.get('CLOUDSCRAPER_BROWSER', None)
        return cls(browser_type)

    def process_request(self, request, spider):
        # Only use cloudscraper for specific domains
        if 'whosampled.com' in request.url:
            try:
                spider.logger.debug(f"Using cloudscraper for: {request.url}")

                # Normalize headers - convert list values to strings
                # This fixes the "Header part must be of type str or bytes, not list" error
                normalized_headers = {}
                for key, value in request.headers.items():
                    # Convert header name to string
                    header_name = key.decode('utf-8') if isinstance(key, bytes) else str(key)

                    # Handle header value based on type
                    if isinstance(value, list):
                        # Take first value from list and ensure it's a string
                        if value:
                            header_value = value[0]
                            if isinstance(header_value, bytes):
                                header_value = header_value.decode('utf-8')
                            normalized_headers[header_name] = str(header_value)
                    elif isinstance(value, bytes):
                        normalized_headers[header_name] = value.decode('utf-8')
                    else:
                        normalized_headers[header_name] = str(value)

                spider.logger.debug(f"Normalized headers: {normalized_headers}")

                # Make the request using cloudscraper with normalized headers
                response = self.scraper.get(
                    request.url,
                    headers=normalized_headers,
                    cookies=request.cookies,
                    allow_redirects=True
                )

                # Create a new headers dictionary without Content-Encoding
                # This fixes the gzip decompression error
                headers_dict = dict(response.headers)
                if 'Content-Encoding' in headers_dict:
                    spider.logger.debug(f"Removing Content-Encoding header: {headers_dict['Content-Encoding']}")
                    del headers_dict['Content-Encoding']

                # Return a properly formatted HtmlResponse
                return HtmlResponse(
                    url=request.url,
                    status=response.status_code,
                    headers=headers_dict,
                    body=response.content,
                    encoding='utf-8',
                    request=request
                )
            except Exception as e:
                spider.logger.error(f"Cloudscraper error for {request.url}: {str(e)}")
                # Log the full exception for debugging
                import traceback
                spider.logger.error(traceback.format_exc())
                return None