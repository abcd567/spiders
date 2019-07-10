"""
-------------------------------------------------
   File Name：     jobbole
   Description :
   Author :       '吴飞鸿'
   date：          2019/4/18
-------------------------------------------------
   Change Activity:
                   2019/4/18:
-------------------------------------------------
"""
__author__ = '吴飞鸿'

from scrapy.http import Request
from urllib import parse
from scrapy_redis.spiders import RedisSpider

class JobboleSpider(RedisSpider):
    name = 'jobbole'

    allowed_domains = ['blog.jobbole.com']

    # 设置此spider下对应的key名字，key内——存储本Spider的数据
    redis_key = 'jobbole:start_urls'

    custom_settings = {
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": True,
    }

    def parse(self, response):
        # do stuff
        """
        1、获取文章列表页钟的文章url并交给scrapy下载后并进行解析
        2、获取下一页的url并交给scrapy进行下载，下载完成后交给parse函数
        """
        # 1、获取文章列表页钟的文章url并交给scrapy下载后并进行解析
        post_nodes = response.css('#archive > div.post:nth-child(n) > div:nth-child(1) > a:nth-child(1)')
        for post_node in post_nodes:
            image_url = post_node.css("img:nth-child(1)::attr(src)").extract_first("")
            post_url = post_node.css('::attr(href)').extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_image_url': image_url},
                          callback=self.parse_detail)
        # 2、获取下一页的url并交给scrapy进行下载，下载完成后交给parse函数
        next_url = response.css('.next::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # 提取文章的具体字段

        """
        """
        # # ArticleItemLoader自定义继承ItemLoader
        # item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        # # item_loader.add_css()
        # # item_loader.add_xpath()
        # # item_loader.add_value()
        # front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        #
        # item_loader.add_css('title', '.entry-header > h1:nth-child(1)::text')
        # item_loader.add_value('url', response.url)
        # item_loader.add_value('url_object_id', get_md5(response.url))
        # item_loader.add_css('create_date', '.entry-meta-hide-on-mobile::text')
        # item_loader.add_value('front_image_url', [front_image_url])
        # item_loader.add_css('praise_nums', '.vote-post-up > h10::text')
        # item_loader.add_css('fav_nums', 'span.btn-bluet-bigger:nth-child(2)::text')
        # item_loader.add_css('comment_nums', 'span.hide-on-480::text')
        # item_loader.add_css('content', '.entry')
        # item_loader.add_css('tags', '.entry-meta-hide-on-mobile > a:nth-child(n)::text')
        #
        # article_item = item_loader.load_item()
        #
        # yield article_item
        pass

