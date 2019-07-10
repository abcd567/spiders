# -*- coding: utf-8 -*-

import os
import sys
# Scrapy settings for ArticleSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ArticleSpider'

SPIDER_MODULES = ['ArticleSpider.spiders']
NEWSPIDER_MODULE = 'ArticleSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ArticleSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True
ROBOTSTXT_OBEY = False  #必须设置为False,关掉robot协议，否则会过滤掉不是robot协议的url

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False
# COOKIES_ENABLED = True
# COOKIES_DEBUG = True


# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'ArticleSpider.middlewares.ArticlespiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'ArticleSpider.middlewares.ArticlespiderDownloaderMiddleware': 543,
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
   # 'ArticleSpider.middlewares.RandomUserAgentMiddleware': 543,
   # 'ArticleSpider.middlewares.RandomProxyMiddleware': 500,
   # 'ArticleSpider.middlewares.JSPageMiddleware': 1,
}


# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   #  pipeline的数字越小，越早进入处理
   # 'ArticleSpider.pipelines.ArticlespiderPipeline': 300,
   # 'scrapy.pipelines.images.ImagesPipeline': 1,
   # 'ArticleSpider.pipelines.JsonWithEncodingPipeline': 2,
   # 'ArticleSpider.pipelines.JsonExporterPipeline': 2,
   # 'ArticleSpider.pipelines.ArticleImagePipeline': 1,
   # 'ArticleSpider.pipelines.MysqlPipeline': 1,
   # 'ArticleSpider.pipelines.MysqlTwistedPipline': 1
   'ArticleSpider.pipelines.ElasticsearchPipeline': 1

}
# 去front_image_url字段找下载图片的路径
IMAGES_URLS_FIELD = "front_image_url"
# 下载的图片本地存储路径
project_dir = os.path.abspath(os.path.dirname(__file__))
IMAGES_STORE = os.path.join(project_dir, 'images')
# 有需要可以设置最小高度和最小宽度等图片数据
# IMAGE_MIN_HEIGHT = 100
# IMAGE_MIN_WIDTH = 100



# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
# fake-useragent 用户代理类型设置
RANDOM_UA_TYPE = "random"

MYSQL_HOST = "192.168.0.107 "
MYSQL_DBNAME = "article_spider"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"

SQL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQL_DATE_FORMAT = "%Y-%m-%d"

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'ArticleSpider'))
