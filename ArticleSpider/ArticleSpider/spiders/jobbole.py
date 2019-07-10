# -*- coding: utf-8 -*-
import re
import datetime

import scrapy
from scrapy.http import Request
from urllib import parse
from scrapy.loader import ItemLoader
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    custom_settings = {
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": True,
    }

    # def __init__(self):
    #     配合middleware.JSPageMiddleware使用
    #     # 当爬虫开始时候，用selenium打开chrome
    #     chrome_options = Options()
    #     chrome_options.add_argument('--no-sandbox')
    #     self.browser = webdriver.Chrome(executable_path='/usr/local/chromedriver/chromedriver', chrome_options=chrome_options)
    #     super(JobboleSpider, self).__init__()
    #     # 当爬虫退出的时候关闭chrome
    #     dispatcher.connect(self.spider_closed, signals.spider_closed)

    handle_httpstatus_list = [404]

    def __init__(self, **kwargs):
        self.fail_url = []
        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)

    # def spider_closed(self, spider):
    #     # 当爬虫退出的时候关闭chrome
    #     print("spider close")
    #     self.browser.quit()

    def handle_spider_closed(self, spider, reason):
        self.crawler.stats.set_value("failed_url", ",".join(self.fail_url))
        pass


    def parse(self, response):

        if response.status == 404:
            self.fail_url.append(response.url)
            self.crawler.stats.inc_value("failed_url")
        """
        1、获取文章列表页钟的文章url并交给scrapy下载后并进行解析
        2、获取下一页的url并交给scrapy进行下载，下载完成后交给parse函数
        """
        # 1、获取文章列表页钟的文章url并交给scrapy下载后并进行解析
        post_nodes = response.css('#archive > div.post:nth-child(n) > div:nth-child(1) > a:nth-child(1)')
        for post_node in post_nodes:
            image_url = post_node.css("img:nth-child(1)::attr(src)").extract_first("")
            post_url = post_node.css('::attr(href)').extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_image_url': image_url}, callback=self.parse_detail)
        # 2、获取下一页的url并交给scrapy进行下载，下载完成后交给parse函数
        next_url = response.css('.next::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # 提取文章的具体字段

        """
        xpath使用
        # 火狐浏览器xpath
        re_seletor = response.xpath('/html/body/div[1]/div[3]/div[1]/div[1]/h1')
        # chrome浏览器xpath
        re_seletor2 = response.xpath('//*[@id="post-114676"]/div[1]/h1')
        # 自己写xpath也可以
        re_seletor3 = response.xpath('//div[@class="entry-header"]/h1/text()')
        """
        # xpath方式

        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")
        # create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract_first("").strip().replace("·", "").strip()
        # praise_nums = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract_first("")
        # fav_nums = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract_first("")
        # match_re = re.match('.*?(\d+).*', fav_nums)
        # if match_re:
        #     fav_nums = match_re.group(1)
        # else:
        #     fav_nums = 0
        #
        # comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first("")
        # match_re = re.match('.*?(\d+).*', comment_nums)
        # if match_re:
        #     comment_nums = match_re.group(1)
        # else:
        #     comment_nums = 0
        #
        # content = response.xpath('//div[@class="entry"]').extract_first("")
        #
        # tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ','.join(tag_list)

        # CSS方式
        # front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        # title = response.css('.entry-header > h1:nth-child(1)::text').extract_first("")
        # create_date = response.css('.entry-meta-hide-on-mobile::text').extract_first("").strip().replace('·', '').strip()
        # praise_nums = response.css('.vote-post-up > h10::text').extract_first("")
        # fav_nums = response.css('span.btn-bluet-bigger:nth-child(2)::text').extract_first("")
        # match_re = re.match('.*?(\d+).*', fav_nums)
        # if match_re:
        #     fav_nums = match_re.group(1)
        # else:
        #     fav_nums = 0
        # comment_nums = response.css('span.hide-on-480::text').extract_first("")
        # match_re = re.match('.*?(\d+).*', comment_nums)
        # if match_re:
        #     comment_nums = match_re.group(1)
        # else:
        #     comment_nums = 0
        # content = response.css('.entry').extract_first("")
        #
        # tag_list = response.css('.entry-meta-hide-on-mobile > a:nth-child(n)::text').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ','.join(tag_list)
        #
        # article_item = JobBoleArticleItem()
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["url"] = response.url
        # article_item["title"] = title
        # try:
        #     create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_nums"] = praise_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["content"] = content
        # article_item["tags"] = tags

        # 通过ItemLoader加载item
        # item_loader = ItemLoader(item=JobBoleArticleItem(), response=response)
        # ArticleItemLoader自定义继承ItemLoader
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        # item_loader.add_css()
        # item_loader.add_xpath()
        # item_loader.add_value()
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图

        item_loader.add_css('title', '.entry-header > h1:nth-child(1)::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('create_date', '.entry-meta-hide-on-mobile::text')
        item_loader.add_value('front_image_url', [front_image_url])
        item_loader.add_css('praise_nums', '.vote-post-up > h10::text')
        item_loader.add_css('fav_nums', 'span.btn-bluet-bigger:nth-child(2)::text')
        item_loader.add_css('comment_nums', 'span.hide-on-480::text')
        item_loader.add_css('content', '.entry')
        item_loader.add_css('tags', '.entry-meta-hide-on-mobile > a:nth-child(n)::text')

        article_item = item_loader.load_item()

        yield article_item

