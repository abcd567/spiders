# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from w3lib.html import remove_tags

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
import MySQLdb
from twisted.enterprise import adbapi
import MySQLdb.cursors

from ArticleSpider.models.es_types import ArticleType

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    # save as .json file. method 1 自定义
    # 函数名都是固定的，settings配置才能识别
    def __init__(self):
        # first : open .json file
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        # second : deal item
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        # close .json file
        self.file.close()


class JsonExporterPipeline(object):
    # save as .json file.method 2 利用scrapy
    # 函数名都是固定的，settings配置才能识别
    def __init__(self):
        # open .json file
        self.file = open('articleExport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        # close .json file
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        # deal with item
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    # 同步方式，只适合少数据入库，大数据会阻塞
    def __init__(self):
        # 连接数据库
        self.conn = MySQLdb.Connect('192.168.0.104', 'root', 'root', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, fav_nums)
            VALUES (%s, %s, %s,%s)
        """
        self.cursor.execute(insert_sql, (item['title'], item['url'], item['create_date'], item['fav_nums']))
        self.conn.commit()


class MysqlTwistedPipline(object):
    # 异步方式，适合大数据不产生阻塞
    def __init__(self, dbpool):
        self.dbpool = dbpool

    # 下面的方法扩展scrapy可以直接用settings.py里的参数值
    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        # adbapi实现异步化操作
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)     # deal exception

    def handle_error(self, failture, item, spider):
        # 处理异步插入的异常
        print(failture)

    def do_insert(self, cursor, item):
        # 执行具体插入
        insert_sql, parmas = item.get_insert_sql()
        cursor.execute(insert_sql, parmas)


class ArticleImagePipeline(ImagesPipeline):
    #
    def item_completed(self, results, item, info):
        image_file_path = ''
        if 'front_image_url' in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        return item


class ElasticsearchPipeline(object):
    # send data to es-server
    def process_item(self, item, spider):
        # item转换为es的数据类型
        item.save_to_es()

        return item
