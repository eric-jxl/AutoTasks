#!/usr/bin/env python3

"""
@Author   : Eric
@license  : Apache Licence
@Datetime : 2024/12/23 12:10
@IDE      : PyCharm
@DESC     :
"""
import os
import requests
import logging

from weather_report import get_access_token
from weather_report import openId
from utils import retry_on_exception

tech_logger = logging.getLogger('tech')
new_template_id = os.environ.get('NEW_TEMPLATE_ID')
Headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}


@retry_on_exception(max_retries=3, initial_delay=1, backoff_factor=2, exceptions=(requests.exceptions.RequestException,))
def get_ipinfo():
    res = requests.get("https://api.vvhan.com/api/ipInfo", headers=Headers)
    data = res.json()
    if data.get('success'):
        info = data.get("info")
        country, prov, city, isp = info.get("country"), info.get(
            "prov"), info.get("city"), info.get("isp")
        return f"{data.get('ip')}, {country}{prov}{city} {isp}"
    return


def common_getinfo(url):
    try:
        res = requests.get(url)
        r = res.json()
        if r.get('success'):
            return r
    except Exception as e:
        tech_logger.error(e)
    else:
        return


class TechInfo(object):

    @staticmethod
    def get_news(url):
        info = common_getinfo(url)
        if info:
            summary = {
                "name": f"{info.get('name','')}-{info.get('subtitle','')}",
                "update_time": info.get("update_time", ''),
                "news": "，".join([f"{n.get('title', '')}--{n.get('hot', '')}" for n in info.get('data', {})])
            }
            return summary
        return info

    def get_toutiao_news(self):
        # 调用get_news方法，传入头条新闻的API地址，获取头条新闻数据
        return self.get_news("https://api.vvhan.com/api/hotlist/toutiao")
    
    @staticmethod
    @retry_on_exception(max_retries=3, initial_delay=1, backoff_factor=2, exceptions=(requests.exceptions.RequestException,))
    def send_news(access_token, news, uri):
        import datetime
        today_str = datetime.date.today().strftime("%Y年%m月%d日")
        for oid in openId.split(','):
            body = {
                "touser": oid.strip(),
                "template_id": new_template_id.strip(),
                "url": uri,
                "data": {
                    "date": {"value": today_str, "color": "#d76c25"},
                    "name": {"value": news.get("name")},
                    "update_time": {"value": news.get("update_time")},
                    "news": {"value": news.get("news"), "color": "#d76c25"},
                    "ipinfo": {"value": get_ipinfo()}
                }
            }
            url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
            res = requests.post(url, json=body)
            rjson = res.json()
            if rjson.get("errcode") == 0:
                tech_logger.info("Weather request OK")
            else:
                tech_logger.error(
                    f"Weather request {rjson['errcode']} {rjson['errmsg']}")


def main():
    access_token = get_access_token()
    t = TechInfo()
    tech = t.get_toutiao_news()
    t.send_news(access_token, tech,
                "https://api.vvhan.com/api/hotlist/toutiao")


if __name__ == '__main__':
    main()
