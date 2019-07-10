"""
-------------------------------------------------
   File Name：     common
   Description :
   Author :       '吴飞鸿'
   date：          2019/4/2
-------------------------------------------------
   Change Activity:
                   2019/4/2:
-------------------------------------------------
"""
__author__ = '吴飞鸿'

import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        # url转化为utf-8编码
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    match_re = re.match('.*?(\d+).*', text)
    if match_re:
        value = int(match_re.group(1))
    else:
        value = 0
    return value

if __name__ == "__main__":
    print(get_md5("http://jobbole.com"))