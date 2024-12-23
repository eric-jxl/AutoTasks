import os
import requests
from bs4 import BeautifulSoup

appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
openId = os.environ.get("OPEN_ID")
weather_template_id = os.environ.get("TEMPLATE_ID")

weather_cache = {}


def get_weather(my_city):
    if my_city in weather_cache:
        return weather_cache[my_city]

    url = "https://www.weather.com.cn/textFC/{}.shtml"
    regions = ["hb", "db", "hd", "hz", "hn", "xb", "xn"]

    for region in regions:
        resp = requests.get(url.format(region))
        soup = BeautifulSoup(resp.content, 'html5lib')
        tables = soup.select("div.conMidtab table")

        for table in tables:
            for tr in table.find_all("tr")[2:]:
                tds = tr.find_all("td")
                city_td = tds[-8]
                this_city = city_td.get_text(strip=True)

                if this_city == my_city:
                    high_temp = tds[-5].get_text(strip=True)
                    low_temp = tds[-2].get_text(strip=True)
                    weather_typ_day = tds[-7].get_text(strip=True)
                    weather_type_night = tds[-4].get_text(strip=True)
                    wind_day = " ".join(tds[-6].stripped_strings)
                    wind_night = " ".join(tds[-3].stripped_strings)

                    temp = f"{low_temp}——{high_temp}摄氏度" if high_temp != "-" else f"{low_temp}摄氏度"
                    weather_typ = weather_typ_day if weather_typ_day != "-" else weather_type_night
                    wind = wind_day if wind_day != "--" else wind_night

                    weather_cache[my_city] = (this_city, temp, weather_typ, wind)
                    return this_city, temp, weather_typ, wind


def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}'
    response = requests.get(url).json()
    return response.get('access_token')


def get_daily_love():
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    sentence = r.json()['returnObj'][0]
    return sentence


def send_weather(access_token, weather):
    import datetime
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    openid_list = list(map(str,list(openId)))
    for oid in openid_list:
        body = {
            "touser": oid.strip(),
            "template_id": weather_template_id.strip(),
            "data": {
                "date": {"value": today_str},
                "region": {"value": weather[0]},
                "weather": {"value": weather[2]},
                "temp": {"value": weather[1]},
                "wind_dir": {"value": weather[3]},
                "today_note": {"value": get_daily_love()},
            }
        }
        url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
        requests.post(url, json=body)


def weather_report(this_city):
    access_token = get_access_token()
    weather = get_weather(this_city)
    send_weather(access_token, weather)


if __name__ == '__main__':
    weather_report("上海")
    weather_report("苏州")
