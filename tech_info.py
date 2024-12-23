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

tech_logger = logging.getLogger('tech')

new_template_id = os.environ.get('NEW_TEMPLATE_ID')

Headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}


def get_ipinfo():
    res = requests.get("https://api.vvhan.com/api/ipInfo", headers=Headers)
    data = res.json()
    if data.get('success'):
        info = data.get("info")
        country, prov, city, isp = info.get("country"), info.get("prov"), info.get("city"), info.get("isp")
        return f"{data.get('ip')}, {country}{prov}{city} {isp}"
    return


def common_getinfo(url):
    res = requests.get(url)
    r = res.json()
    if r.get('success'):
        return r
    return


class TechInfo(object):

    @staticmethod
    def get_news(url):
        info = common_getinfo(url)
        if info:
            summary = {
                "name": f"{info.get('name')}-{info.get('subtitle')}",
                "update_time": info.get("update_time"),
                "news": "，".join([f"{n.get('title', '')}--{n.get('hot', '')}" for n in info.get('data')])
            }
            return summary
        return info

    def get_douyin_new(self):
        return self.get_news("https://api.vvhan.com/api/hotlist/douyinHot")

    def get_tech_news(self):
        return self.get_news("https://api.vvhan.com/api/hotlist/itNews")

    @staticmethod
    def send_news(access_token, news, uri):
        import datetime
        today_str = datetime.date.today().strftime("%Y年%m月%d日")
        for oid in openId.split(','):
            body = {
                "touser": oid.strip(),
                "template_id": new_template_id.strip(),
                "url": uri,
                "data": {
                    "date": {"value": today_str, "color": "#173177"},
                    "name": {"value": news.get("name"), "color": "#173177"},
                    "update_time": {"value": news.get("update_time"), "color": "#173177"},
                    "news": {"value": news.get("news"), "color": "#173177"},
                    "ipinfo": {"value": get_ipinfo(), "color": "#173177"}
                }
            }
            url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
            res = requests.post(url, json=body)
            rjson = res.json()
            if rjson.get("errcode") == 0:
                tech_logger.info("Weather request OK")
            else:
                tech_logger.error(f"Weather request {rjson['errcode']} {rjson['errmsg']}")


def main():
    access_token = get_access_token()
    t = TechInfo()
    douyin = t.get_douyin_new()
    tech = t.get_tech_news()
    t.send_news(access_token, douyin, "https://api.vvhan.com/api/hotlist/douyinHot")
    t.send_news(access_token, tech, "https://api.vvhan.com/api/hotlist/itNews")


if __name__ == '__main__':
    main()
