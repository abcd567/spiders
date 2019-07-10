# -*- coding: utf-8 -*-
import time
import os
import pickle
import datetime
import re

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from ArticleSpider.settings import BASE_DIR
from ArticleSpider.items import LagouJobItem, LagouJobItemLoader
from ArticleSpider.utils.common import get_md5

class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['http://www.lagou.com/']

    custom_settings = {
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": True,
    }

    headers = {
        "HOST": "www.lagou.com",
        "Referer": "https://www.lagou.com",
        "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }

    rules = (
        Rule(LinkExtractor(allow=(r'zhaopin/.*', )), follow=True),
        Rule(LinkExtractor(allow=(r'gongsi/j\d+.html*', )), follow=True),
        Rule(LinkExtractor(allow=(r'jobs/\d+.html', )), callback='parse_item', follow=True),
    )
    handle_httpstatus_list = [302]

    redirect_url = []

    def parse_item(self, response):
        # item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        # return item
        # if 'utrack/track' in response.url:
        #     # 本想解决302重定向问题，但此法无效
        #     num = re.match('.*2F(\d+).html.*', response.url)
        #     num = str(num.group(1))
        #     url = 'https://www.lagou.com/jobs/' + num + '.html'
        #     print(url)
        #     time.sleep(2)
        #     return scrapy.Request(url, dont_filter=True, headers=self.headers)
        if response.status == 302:
            self.redirect_url.append(response.url)
            self.crawler.stats.inc_value("redirected_url")

        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css('title', 'span.name:nth-child(2)::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('salary', '.job_request .salary::text')
        item_loader.add_xpath('job_city', '//*[@class="job_request"]/p/span[2]/text()')
        item_loader.add_xpath('work_years', '//*[@class="job_request"]/p/span[3]/text()')
        item_loader.add_xpath('degree_need', '//*[@class="job_request"]/p/span[4]/text()')
        item_loader.add_xpath('job_type', '//*[@class="job_request"]/p/span[5]/text()')
        item_loader.add_css('tags', '.position-label li::text')
        item_loader.add_css('publish_time', '.publish_time::text')
        item_loader.add_css('job_advantage', '.job-advantage p::text')
        item_loader.add_css('job_desc', '.job_bt div')
        item_loader.add_css('job_addr', '.work_addr')
        item_loader.add_css('company_name', '#job_company dt a img::attr(alt)')
        item_loader.add_css('company_url', '#job_company dt a::attr(href)')
        item_loader.add_value('crawl_time', datetime.datetime.now())

        job_item = item_loader.load_item()

        return job_item

    def start_requests(self):
        # 使用拉钩cookie直接登录
        # cookies = []
        # if os.path.exists(BASE_DIR+'/cookies/lagou.cookie'):
        #     cookies = pickle.load(open(BASE_DIR+'/cookies/lagou.cookie', 'rb'))

        # if not cookies:
        # selenium模拟登录拉钩
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        browser = webdriver.Chrome(executable_path='/usr/local/chromedriver/chromedriver',
                                   chrome_options=chrome_options)

        try:
            browser.maximize_window()
        except:
            pass
        browser.get('https://passport.lagou.com/login/login.html')
        time.sleep(5)
        try:
            browser.find_element_by_css_selector('form.active > div:nth-child(1) > input:nth-child(1)').send_keys(Keys.CONTROL + 'a')
            browser.find_element_by_css_selector('form.active > div:nth-child(1) > input:nth-child(1)').send_keys('15986744115')
            browser.find_element_by_css_selector('form.active > div:nth-child(2) > input:nth-child(1)').send_keys(Keys.CONTROL + 'a')
            browser.find_element_by_css_selector('form.active > div:nth-child(2) > input:nth-child(1)').send_keys('******')
            browser.find_element_by_css_selector('.sense_login_password > input:nth-child(1)').click()
            # 此处等待时间,输入验证码
            # time.sleep(15)
            time.sleep(5)
        except:
            pass
        cookies = browser.get_cookies()
        # pickle.dump(cookies, open(BASE_DIR+'/cookies/lagou.cookie', 'wb'))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict, headers=self.headers)

