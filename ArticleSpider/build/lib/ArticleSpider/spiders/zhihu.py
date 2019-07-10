# -*- coding: utf-8 -*-
import time
import re
import pickle
import base64
try:
    # python3
    from urllib import parse
except:
    # python2
    import urlparse
import json
import datetime

import scrapy
from scrapy.loader import ItemLoader
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
# from mouse import move, click
import pyautogui

from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }

    custom_settings = {
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": True,
    }

    # question的answer请求url  {0}:question_id  {1}:offset
    start_answer_urls = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics&offset={1}&limit=5&sort_by=default&platform=desktop"

    def parse(self, response):
        """
        提取出html页面中的所有url    并跟踪这些url进行进一步爬取
        如果提取的url中格式为 /question/xxx 就下载之后进入解析函数
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        # text = response.text
        for url in all_urls:
            match_obj = re.match('(.*zhihu.com/question/(\d+))(/|$).*', url)
            if match_obj:
                # 如果提取到url是question页面则交由提取函数进行提取
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)

                yield scrapy.Request(url=request_url, headers=self.headers,
                                     meta={'question_id': question_id}, callback=self.parse_question)
                # yield scrapy.Request(url=request_url, headers=self.headers, callback=self.parse)
            else:
                # 如果不是question页面，则对当前页面进一步跟踪
                yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)


    def parse_question(self, response):
        """
        从question页面提取question item
        """
        question_id = response.meta.get('question_id', '')

        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css('title', 'h1.QuestionHeader-title:nth-child(2)::text')
        item_loader.add_css('content', '.QuestionHeader-detail')
        item_loader.add_value('url', response.url)
        item_loader.add_value('zhihu_id', question_id)
        item_loader.add_css('answer_num', '.List-headerText > span:nth-child(1)::text')
        item_loader.add_css('comments_num', '.QuestionHeader-Comment > button:nth-child(1)::text')
        item_loader.add_css('watch_user_num', '.NumberBoard-itemValue::text')
        item_loader.add_css('topics', '.QuestionHeader-topics .Popover > div::text')

        question_item = item_loader.load_item()

        yield scrapy.Request(url=self.start_answer_urls.format(question_id, 0), headers=self.headers, callback=self.parse_answer)

        yield question_item

    def parse_answer(self, response):
        """
        用json提取answer
        """
        # 有无下一个回答
        ans_json = json.loads(response.text)
        is_end = ans_json['paging']['is_end']
        totals_answer = ans_json['paging']['totals']
        next_url = ans_json['paging']['next']

        # 提取answer字段
        for answer in ans_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id']
            answer_item['content'] = answer['content'] if 'content' in answer else None
            answer_item['praise_num'] = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(url=next_url, headers=self.headers, callback=self.parse_answer)
        pass

    def start_requests(self):
        """
        用selenium完成知乎自动登陆
        """
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
        browser = webdriver.Chrome(executable_path='/usr/local/chromedriver/chromedriver',
                                   chrome_options=chrome_options)
        try:
            browser.maximize_window()
        except:
            pass

        browser.get("https://www.zhihu.com/signin")
        try:
            # 未登录知乎
            time.sleep(3)
            # 清空默认填充值,clear()方法失效，使用control+a全选再输入,全选之前先等待3秒让浏览器加载了默认填充值
            browser.find_element_by_css_selector('.SignFlow-accountInput > input:nth-child(1)').send_keys(Keys.CONTROL + "a")
            browser.find_element_by_css_selector('.SignFlow-accountInput > input:nth-child(1)').send_keys("15986744115")

            browser.find_element_by_css_selector('div.SignFlowInput:nth-child(1) > div:nth-child(1) > input:nth-child(1)').send_keys(Keys.CONTROL + "a")
            browser.find_element_by_css_selector('div.SignFlowInput:nth-child(1) > div:nth-child(1) > input:nth-child(1)').send_keys('29q82q8t7q')
            # css捕获’登陆‘按钮并鼠标点击
            browser.find_element_by_css_selector('button.Button:nth-child(5)').click()

            time.sleep(5)
            login_success = False
            while not login_success:
                try:
                    notify_element = browser.find_element_by_css_selector('.Zi--Bell > path:nth-child(1)')
                    login_success = True
                except:
                    pass

                try:
                    english_captcha_element = browser.find_element_by_class_name('Captcha-englishImg')
                except:
                    english_captcha_element = None

                try:
                    chinese_cptcha_element = browser.find_element_by_class_name('Captcha-chineseImg')
                except:
                    chinese_cptcha_element = None

                if chinese_cptcha_element:
                    element_position = chinese_cptcha_element.location
                    x_relative = element_position['x']
                    y_relative = element_position['y']
                    # browser_navigtion_panel_height = browser.execute_script(
                    #     'return window.outerHeight - window.innerHeight;'
                    # )
                    browser_navigtion_panel_height = 103

                    base64_text = chinese_cptcha_element.get_attribute('src')
                    code = base64_text.replace('data:image/jpg;base64,', '').replace('%0A', '')
                    fh = open('yzm_cn.jpeg', 'wb')
                    fh.write(base64.b64decode(code))
                    fh.close()

                    from zheye import zheye
                    z = zheye()
                    try:
                        positions = z.Recognize('yzm_cn.jpeg')
                    except:
                        time.sleep(3)
                        browser.find_element_by_css_selector('.SignFlow-accountInput > input:nth-child(1)').send_keys(
                            Keys.CONTROL + "a")
                        browser.find_element_by_css_selector('.SignFlow-accountInput > input:nth-child(1)').send_keys(
                            "15986744115")

                        browser.find_element_by_css_selector(
                            'div.SignFlowInput:nth-child(1) > div:nth-child(1) > input:nth-child(1)').send_keys(
                            Keys.CONTROL + "a")
                        browser.find_element_by_css_selector(
                            'div.SignFlowInput:nth-child(1) > div:nth-child(1) > input:nth-child(1)').send_keys('29q82q8t7q')
                        # css捕获’登陆‘按钮并鼠标点击
                        browser.find_element_by_css_selector('button.Button:nth-child(5)').click()
                        time.sleep(5)

                        continue

                    last_position = []
                    if len(positions) == 2:
                        if positions[0][1] > positions[1][1]:
                            last_position.append([positions[1][1], positions[1][0]])
                            last_position.append([positions[0][1], positions[0][0]])
                        else:
                            last_position.append([positions[0][1], positions[0][0]])
                            last_position.append([positions[1][1], positions[1][0]])

                        first_position = [int(last_position[0][0] / 2), int(last_position[0][1] / 2)]
                        second_position = [int(last_position[1][0] / 2), int(last_position[1][1] / 2)]

                        time.sleep(1)
                        pyautogui.moveTo(x_relative + first_position[0],
                                         y_relative + browser_navigtion_panel_height + first_position[1], duration=0.5)
                        pyautogui.click()

                        time.sleep(1)

                        pyautogui.moveTo(x_relative + second_position[0],
                                         y_relative + browser_navigtion_panel_height + second_position[1], duration=0.5)
                        pyautogui.click()

                    else:
                        last_position.append([positions[0][1], positions[0][0]])

                        first_position = [int(last_position[0][0] / 2), int(last_position[0][1] / 2)]

                        time.sleep(1)
                        pyautogui.moveTo(x_relative + first_position[0],
                                         y_relative + browser_navigtion_panel_height + first_position[1], duration=0.5)
                        pyautogui.click()

                if english_captcha_element:
                    base64_text = english_captcha_element.get_attribute('src')
                    code = base64_text.replace('data:image/jpg;base64,', '').replace('%0A', '').replace(r'\n', '')
                    fh = open('yzm_en.jpeg', 'wb')
                    fh.write(base64.b64decode(code))
                    fh.close()

                    from tool.yundama_requests import YDMHttp
                    yundama = YDMHttp('915263031', 'slzkszkbjz', 7346, '8da3657e176de5e60bce4bf449eae130')
                    code = yundama.decode('yzm_en.jpeg', 5000, 60)
                    while True:
                        if code == '':
                            code = yundama.decode('yzm_en.jpeg', 5000, 60)
                        else:
                            break

                    browser.find_element_by_xpath(
                        '//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[3]/div/div/div[1]/input').send_keys(Keys.CONTROL + "a")
                    browser.find_element_by_xpath(
                        '//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[3]/div/div/div[1]/input').send_keys(code)

                if english_captcha_element or chinese_cptcha_element:
                    # 再次输入用户名和密码
                    time.sleep(3)
                    browser.find_element_by_css_selector('.SignFlow-accountInput > input:nth-child(1)').send_keys(
                        Keys.CONTROL + "a")
                    browser.find_element_by_css_selector('.SignFlow-accountInput > input:nth-child(1)').send_keys(
                        "15986744115")

                    browser.find_element_by_css_selector(
                        'div.SignFlowInput:nth-child(1) > div:nth-child(1) > input:nth-child(1)').send_keys(
                        Keys.CONTROL + "a")
                    browser.find_element_by_css_selector(
                        'div.SignFlowInput:nth-child(1) > div:nth-child(1) > input:nth-child(1)').send_keys('29q82q8t7q')
                    # css捕获’登陆‘按钮并鼠标点击
                    browser.find_element_by_css_selector('button.Button:nth-child(5)').click()

                time.sleep(5)
        except:
            # 已登录 不做任何操作
            pass

        cookies = browser.get_cookies()
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]








    # def start_requests(self):
    #     """
    #
    #     """
    #     # 直接通过cookie登陆
    #     cookies = pickle.load(open('/home/deep-scrapy/pyprojects/ArticleSpider/cookies/zhihu.cookie', 'rb'))
    #     cookie_dict = {}
    #     for cookie in cookies:
    #         cookie_dict[cookie['name']] = cookie['value']
    #
    #     return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
    #
    #     # linux系统需要加上启动项
    #     # options = Options()
    #     # options.add_argument('--headless')    # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    #     # options.add_argument('--no-sandbox')    # 解决DevToolsActivePort文件不存在的报错
    #     # options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
    #     # options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    #     # options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    #     # options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    #     # """ 手动启动chrome浏览器并在9222端口上监听 """
    #     # options.add_argument("--disable-extensions")
    #     # options.add_argument('--no-sandbox')
    #     # options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    #     # chrome_options = Options()
    #     # chrome_options.add_argument('--no-sandbox')
    #     # chrome_options.add_argument('--disable-extensions')
    #     # chrome_options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
    #     #
    #     # browser = webdriver.Chrome(executable_path='/usr/local/chromedriver/chromedriver',
    #     #                            chrome_options=chrome_options)
    #
    #
    #     # browser.get("https://www.zhihu.com/signin")
    #     # # 清空默认填充值,clear()方法失效，使用control+a全选再输入,全选之前先等待3秒让浏览器加载了默认填充值
    #     # time.sleep(3)
    #     #
    #     # # browser.find_element_by_css_selector('.SignFlow-accountInput > input:nth-child(1)').clear()
    #     # browser.find_element_by_css_selector('.SignFlow-accountInput > input:nth-child(1)').send_keys(Keys.CONTROL + "a")
    #     # browser.find_element_by_css_selector('.SignFlow-accountInput > input:nth-child(1)').send_keys("15986744115")
    #     #
    #     # # browser.find_element_by_css_selector('div.SignFlowInput:nth-child(1) > div:nth-child(1) > input:nth-child(1)').clear()
    #     # browser.find_element_by_css_selector(
    #     #     'div.SignFlowInput:nth-child(1) > div:nth-child(1) > input:nth-child(1)').send_keys(Keys.CONTROL + "a")
    #     # browser.find_element_by_css_selector('div.SignFlowInput:nth-child(1) > div:nth-child(1) > input:nth-child(1)').send_keys('slzkszkbjz123')
    #     #
    #     # # 如果捕获css的鼠标点击有问题，可以通过mouse库移动鼠标到指定位置点击
    #     # # time.sleep(3)
    #     # # move(520, 520)
    #     # # click()
    #     # # css捕获’登陆‘按钮并鼠标点击
    #     # browser.find_element_by_css_selector('button.Button:nth-child(5)').click()
    #
    #     # 获取cookie,为后续直接通过cookie登陆做准备
    #     # browser.get('http://www.zhihu.com/')
    #     # cookies = browser.get_cookies()
    #     #
    #     # pickle.dump(cookies, open('/home/deep-scrapy/pyprojects/ArticleSpider/cookies/zhihu.cookie', 'wb'))
    #     # cookie_dict = {}
    #     # for cookie in cookies:
    #     #     cookie_dict[cookie['name']] = cookie['value']
    #     #
    #     # return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
    #
    #     # time.sleep(60)