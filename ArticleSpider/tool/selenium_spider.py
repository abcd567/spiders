"""
-------------------------------------------------
   File Name：     selenium_spider
   Description :
   Author :       '吴飞鸿'
   date：          2019/4/15
-------------------------------------------------
   Change Activity:
                   2019/4/15:
-------------------------------------------------
"""
__author__ = '吴飞鸿'
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import pyautogui

# chrome_options = Options()
# chrome_options.add_argument('--no-sandbox')
# browser = webdriver.Chrome(executable_path='/usr/local/chromedriver/chromedriver', chrome_options=chrome_options)
#
# browser.get("https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.51.786d39620u2bwz&id=580609665095&user_id=430395561&cat_id=2&is_b=1&rn=cbc745c40ee3d5d662a7f61a38a783f5")
# try:
#     browser.maximize_window()
# except:
#     pass
# time.sleep(5)
# print(browser.page_source)


# pyautogui.moveTo(752, 327, duration=1)
# pyautogui.click()
# for i in range(2):
#     browser.execute_script('window.scrollTo(0, document.body.scrollHeight); var lengOfPage=document.body.scrollHeight; return lengOfPage;')
#     # pyautogui.scroll(-500)
#     time.sleep(1)

# 不加载图片
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--no-sandbox')
#
# #此法无效
# # prefs = {"profile.managed_default_content_settings.image": 2}
# # chrome_options.add_experimental_option("prefs", prefs)
# # 改用：
# chrome_options.add_argument('blink-settings=imagesEnabled=false')
#
# browser = webdriver.Chrome(executable_path='/usr/local/chromedriver/chromedriver', chrome_options=chrome_options)
#
# browser.get("https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.51.786d39620u2bwz&id=580609665095&user_id=430395561&cat_id=2&is_b=1&rn=cbc745c40ee3d5d662a7f61a38a783f5")
# try:
#     browser.maximize_window()
# except:
#     pass
# time.sleep(5)
# pyautogui.moveTo(752, 327, duration=1)
# pyautogui.click()
# t_selector = Selector(text=browser.page_source)
# price = t_selector.css('span.tm-price::text').extract()[0]
# print(price)
# browser.quit()

# 不显示界面
# from pyvirtualdisplay import Display
# display = Display(visible=0, size=(800, 600))
# display.start()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(executable_path='/usr/local/chromedriver/chromedriver', chrome_options=chrome_options)
browser.get("https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.51.786d39620u2bwz&id=580609665095&user_id=430395561&cat_id=2&is_b=1&rn=cbc745c40ee3d5d662a7f61a38a783f5")
time.sleep(10)
# browser.find_element_by_xpath('//*[@id="sufei-dialog-close"]').click()
print(browser.page_source)
t_selector = Selector(text=browser.page_source)
price = t_selector.css('span.tm-price::text').extract()[0]
print(price)
pass