# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re

from w3lib.html import remove_tags
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from elasticsearch_dsl.connections import connections
import redis

from ArticleSpider.utils.common import extract_num
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
from ArticleSpider.models.es_types import ArticleType


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    # 以title为例value = title的实际值
    return value + '-jobbole'


def date_convert(value):
    value = value.strip().replace("·", "").strip()
    try:
        date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        date = datetime.datetime.now().date()
    return date


def get_nums(value):
    match_re = re.match('.*?(\d+).*', value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    if "评论" in value:
        return ''
    else:
        return value


def return_value(value):
    return value


# 与ElasticSearch进行连接,生成搜索建议
es = connections.create_connection(ArticleType, hosts=["192.168.0.103"], timeout=200)
# es = connections.create_connection(ArticleType)
def gen_suggest(index, info_tuple):
    # 根据字符串生成建议数组，并赋予权重
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # text不为空，调用es _analyze接口进行分词
            # words = es.indices.analyze(index="jobbole2",
            #                            body={"analyzer": "ik_max_word", "text": "{0}".format(text)},
            #                            params={'filter': ["lowercase"]})
            words = es.indices.analyze(index=index._index._name,
                                       body={"analyzer": "ik_max_word", "text": "{0}".format(text)})
            analyzed_word = set([result["token"] for result in words["tokens"] if len(result["token"]) > 1])
            new_words = analyzed_word - used_words
            used_words.update(words)
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests


class ArticleItemLoader(ItemLoader):
    # ArticleItemLoader自定义继承ItemLoader
    default_output_processor = TakeFirst()

redis_cli = redis.StrictRedis(host="localhost")

class JobBoleArticleItem(scrapy.Item):
    # input_processor : 输入预处理
    # output_processor: 输出格式处理器
    title = scrapy.Field(
        input_processor=MapCompose(add_jobbole)
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        # 覆盖掉默认take_first，保持list
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join('，')
    )

    def get_insert_sql(self):
        # 执行具体插入
        insert_sql = """
            insert into jobbole_article(title, url, url_object_id, front_image_url, create_date, 
                fav_nums, praise_nums, comment_nums, content, tags
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s)
            ON DUPLICATE KEY UPDATE fav_nums = VALUES(fav_nums), praise_nums = VALUES(praise_nums), 
            comment_nums = VALUES(comment_nums)
        """
        # ON DUPLICATE KEY UPDATE fav_nums = VALUES(fav_nums), praise_nums = VALUES(praise_nums), comment_nums = VALUES(comment_nums)

        params = (self['title'], self['url'], self['url_object_id'], self['front_image_url'], self['create_date'],
                  self['fav_nums'],
                  self['praise_nums'], self['comment_nums'], self['content'], self['tags'])

        return insert_sql, params


    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.create_date = self['create_date']
        article.content = remove_tags(self['content'])
        article.front_image_url = self['front_image_url']
        article.front_image_path = self['front_image_path'] if "front_image_path" in self else None
        article.praise_nums = self['praise_nums']
        article.fav_nums = self['praise_nums']
        article.comment_nums = self['praise_nums']
        article.tags = self['tags']
        article.url = self['url']
        article.meta.id = self["url_object_id"]

        article.suggest = gen_suggest(ArticleType, ((article.title, 10), (article.tags, 7)))

        article.save()

        redis_cli.incr("jobbole_count")

        return


class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content, 
                answer_num, comments_num, watch_user_num, click_num, crawl_time
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num),
            comments_num=VALUES(comments_num), watch_user_num=VALUES(watch_user_num),
            click_num=VALUES(click_num)
        """
        # 另一种处理itemloader（返回原始数据是list）的方法
        zhihu_id = self['zhihu_id'][0]
        topics = '，'.join(self['topics'])
        url = self['url'][0]
        title = self['title'][0]
        content = self['content'][0]
        answer_num = extract_num(''.join(self['answer_num']))
        comments_num = extract_num(''.join(self['comments_num']))
        watch_user_num = extract_num(self['watch_user_num'][0].replace(',', ''))
        click_num = extract_num(self['watch_user_num'][1].replace(',', ''))
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content,
                  answer_num, comments_num, watch_user_num, click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的答案item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, 
                praise_num, comments_num, create_time, update_time, crawl_time
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), praise_num=VALUES(praise_num),
            comments_num=VALUES(comments_num), update_time=VALUES(update_time)
        """
        # 将长串数字秒数转化为当前时间
        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)

        parmas = (self['zhihu_id'], self['url'], self['question_id'],
                  self['author_id'], self['content'], self['praise_num'],
                  self['comments_num'], create_time, update_time,
                  self['crawl_time'].strftime(SQL_DATETIME_FORMAT)
        )
        return insert_sql, parmas


class LagouJobItemLoader(ItemLoader):
    # ArticleItemLoader自定义继承ItemLoader
    default_output_processor = TakeFirst()


def remove_splash(value):
    # 去掉工作城市的斜线
    return value.replace('/', '')


def handle_jobaddr(value):
    # 处理地址
    addr_list = value.split('\n')
    addr_list = [item.strip() for item in addr_list if item.strip() != '查看地图']
    return ''.join(addr_list)


class LagouJobItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(',')
    )
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(remove_tags),
    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary, job_city, 
                work_years, degree_need, job_type, publish_time, tags,
                job_advantage, job_desc, job_addr, company_url, company_name, 
                crawl_time)
            VALUES (%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,
                    %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
        """

        parmas = (
            self['title'], self['url'], self['url_object_id'], self['salary'], self['job_city'],
            self['work_years'], self['degree_need'], self['job_type'], self['publish_time'], self['tags'],
            self['job_advantage'], self['job_desc'], self['job_addr'], self['company_url'], self['company_name'],
            self['crawl_time'].strftime(SQL_DATETIME_FORMAT)
        )

        return insert_sql, parmas