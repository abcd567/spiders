"""
-------------------------------------------------
   File Name：     es_types
   Description :
   Author :       '吴飞鸿'
   date：          2019/4/24
-------------------------------------------------
   Change Activity:
                   2019/4/24:
-------------------------------------------------
"""
__author__ = '吴飞鸿'

from datetime import datetime

from elasticsearch_dsl import Document, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

start_connect_time = datetime.now()
try:
    connections.create_connection(hosts=['192.168.0.103:9200'], timeout=200)
    success_connect_time = datetime.now()
    print("success!use {0}s".format(success_connect_time - start_connect_time))
except:
    fail_connect_time = datetime.now()
    print("fail!use {0}s".format(fail_connect_time - start_connect_time))


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class ArticleType(Document):
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    praise_nums = Integer()
    fav_nums = Integer()
    comment_nums = Integer()
    content = Text(analyzer="ik_smart")
    tags = Text(analyzer="ik_smart")

    class Index:
        # 存放位置
        name = 'jobbole'
        settings = {
            "number_of_shards": 5,
        }


if __name__ == "__main__":
    ArticleType.init()
    pass