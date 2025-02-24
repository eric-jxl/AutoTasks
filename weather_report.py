import os
import requests
import logging
from bs4 import BeautifulSoup

weather_logger = logging.getLogger("weather")

appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
openId = os.environ.get("OPEN_ID")
weather_template_id = os.environ.get("TEMPLATE_ID")
AMP_KEY = os.environ.get("AMP_KEY")


def get_weather(city):

    url = f"https://restapi.amap.com/v3/weather/weatherInfo"
    req = requests.get(
        url, params={"key": AMP_KEY, "city": city, "output": "json"})
    if req.status_code != 1:
        weather_logger.error(
            f"Request failed with status code {req.status_code}")
    return req.json().get('lives')[0]


def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}'
    response = requests.get(url).json()
    return response.get('access_token')


def get_daily_love():
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    sentence = r.json()['returnObj'][0]
    return sentence


def send_weather(access_token, weather: dict):
    import datetime
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    for oid in openId.split(','):
        body = {
            "touser": oid.strip(),
            "template_id": weather_template_id.strip(),
            "data": {
                "date": {"value": today_str},
                "region": {"value": weather.get('province') + weather.get('city')},
                "weather": {"value": weather.get('weather')},
                "temp": {"value": weather.get('temperature')},
                "wind_dir": {"value": f"{weather.get('winddirection')}风，风力{weather.get('windpower')}级,湿度:{weather.get('humidity_float')}"},
                "today_note": {"value": get_daily_love(), "color": "#d76c25"},
            }
        }
        url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
        res = requests.post(url, json=body)
        rjson = res.json()
        if rjson.get("errcode") == 0:
            weather_logger.info("Weather request OK")
        else:
            weather_logger.error(
                f"Weather request {rjson['errcode']} {rjson['errmsg']}")


def weather_report(this_city):
    access_token = get_access_token()
    weather = get_weather(this_city)
    send_weather(access_token, weather)


if __name__ == '__main__':
    weather_report("上海")
    weather_report("苏州")
