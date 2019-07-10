"""
-------------------------------------------------
   File Name：     templateTest
   Description :
   Author :       '吴飞鸿'
   date：          2019/4/1
-------------------------------------------------
   Change Activity:
                   2019/4/1:
-------------------------------------------------
"""
__author__ = '吴飞鸿'
import sys
import os

from scrapy.cmdline import execute


# print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy', 'crawl', 'jobbole'])

