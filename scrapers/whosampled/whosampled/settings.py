# Scrapy settings for whosampled project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "whosampled"

SPIDER_MODULES = ["whosampled.spiders"]
NEWSPIDER_MODULE = "whosampled.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.0.0 Safari/537.36',
]


# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 10  # Base delay between requests
RANDOMIZE_DOWNLOAD_DELAY = True  # Add randomness to the delay
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
#CONCURRENT_REQUESTS_PER_IP = 16

RANDOM_DELAY = [10, 20]

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "whosampled.middlewares.WhosampledSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # Disable the default user agent middleware
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,

   # Add custom middlewares
   'whosampled.middlewares.CloudflareMiddleware': 100,  # First, try to bypass Cloudflare,
   'whosampled.middlewares.RandomUserAgentMiddleware': 400,
   'whosampled.middlewares.RequestHeadersMiddleware': 410,
   'whosampled.middlewares.ProxyMiddleware': 420,
   'whosampled.middlewares.RandomDelayMiddleware': 430,

   # Configure the built-in retry middleware
   'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
}

PROXY_LIST = [
    'http://93.157.12.234:8080',
    'http://222.127.248.78:8082',
    'http://103.41.88.182:83',
    'http://185.196.68.106:3128',
    'http://36.94.232.177:3113'
]

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "whosampled.pipelines.WhoSampledPipeline": 300,
   "whosampled.pipelines.JsonWriterPipeline": 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 20
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 120
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# DEPTH_LIMIT = 10

LOG_LEVEL = "INFO"

RETRY_ENABLED = True
RETRY_TIMES = 5  # Number of retries
RETRY_HTTP_CODES = [403, 500, 502, 503, 504, 408, 429]
RETRY_PRIORITY_ADJUST = -2  # Lower priority for retries

# Fix compression error
COMPRESSION_ENABLED = False

# Enable DNS cache
DNSCACHE_ENABLED = True