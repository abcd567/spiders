"""
-------------------------------------------------
   File Name：     zheye_test
   Description :
   Author :       '吴飞鸿'
   date：          2019/4/7
-------------------------------------------------
   Change Activity:
                   2019/4/7:
-------------------------------------------------
"""
__author__ = '吴飞鸿'


from zheye import zheye
z = zheye()
positions = z.Recognize('/home/deep-scrapy/pyprojects/ArticleSpider/tool/zhihu_captcha/a.gif')

last_position = []
if len(positions) == 2:
    if positions[0][1] > positions[1][1]:
        last_position.append([positions[1][1], positions[1][0]])
        last_position.append([positions[0][1], positions[0][0]])
    else:
        last_position.append([positions[0][1], positions[0][0]])
        last_position.append([positions[1][1], positions[1][0]])
else:
    last_position.append([positions[0][1], positions[0][0]])
print(positions)
print(last_position)
