"""
-------------------------------------------------
   File Name：     text
   Description :
   Author :       '吴飞鸿'
   date：          2019/4/27
-------------------------------------------------
   Change Activity:
                   2019/4/27:
-------------------------------------------------
"""
__author__ = '吴飞鸿'

import redis


redis_cli = redis.StrictRedis()
redis_cli.incr("jobbole_count")