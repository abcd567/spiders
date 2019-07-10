"""
-------------------------------------------------
   File Name：     crawl_xici_ip
   Description :
   Author :       '吴飞鸿'
   date：          2019/4/14
-------------------------------------------------
   Change Activity:
                   2019/4/14:
-------------------------------------------------
"""
__author__ = '吴飞鸿'


import requests
from scrapy.selector import Selector
import MySQLdb


conn = MySQLdb.connect(host="192.168.0.107 ", user="root", passwd="root", db="article_spider", charset='utf8')
cursor = conn.cursor()


def crawl_ips():
    # 爬取西刺IP代理
    headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"}
    for i in range(3646):
        re = requests.get('https://www.xicidaili.com/nn/{0}'.format(i), headers=headers)

        selector = Selector(text=re.text)
        all_tr = selector.css('#ip_list tr')

        ip_list = []
        for tr in all_tr[1:]:
            speed_bar = tr.css('.bar::attr(title)').extract_first()
            speed = 0
            if speed_bar:
                speed = float(speed_bar.split('秒')[0])
            all_text = tr.css('td::text').extract()
            ip = all_text[0]
            port = all_text[1]
            proxy_type = all_text[5] if 'HTTP' in all_text[5] else all_text[4]
            remain_time = all_text[7] if 'HTTP' in all_text[5] else all_text[6]
            if '分钟' not in remain_time:
                ip_list.append((ip, port, proxy_type, speed, remain_time))

        for ip_info in ip_list:
            cursor.execute(
                "insert  proxy_ip(ip, port, proxy_type, speed, remain_time) VALUES('{0}', '{1}', '{2}', {3}, '{4}') ON DUPLICATE KEY UPDATE speed=VALUES(speed), remain_time=VALUES(remain_time)".format(
                    ip_info[0], ip_info[1], ip_info[2], ip_info[3], ip_info[4]
                )
            )
            conn.commit()


class GetIP(object):
    def delete_ip(self, ip):
        # 从数据库中删除无效的ip
        delete_sql = """
            delete from proxy_ip where ip='{0}'
        """.format(ip)

        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port, proxy_type):
        # 判断IP时候可用
        http_url = "http://www.baidu.com"
        proxy_url = "{0}://{1}:{2}".format(proxy_type, ip, port)
        proxy_dict = {}
        try:
            if proxy_type == 'HTTP':
                proxy_dict = {
                    'http': proxy_url
                }
            elif proxy_type == 'HTTPS':
                proxy_dict = {
                    'https': proxy_url
                }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port (ip或端口无效)")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port (ip或端口无效)")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        # 从数据库中随机取出一个可用ip
        random_sql = """
            SELECT ip, port,proxy_type,speed FROM proxy_ip
        ORDER BY RAND()
        LIMIT 1
        """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            proxy_type = ip_info[2]
            speed = ip_info[3]

            judge_re = self.judge_ip(ip, port, proxy_type)
            if judge_re:
                return "{0}://{1}:{2}".format(proxy_type, ip, port)
            else:
                return self.get_random_ip()


if __name__ == "__main__":
    crawl_ips()

    # get_ip = GetIP()
    # get_ip.get_random_ip()