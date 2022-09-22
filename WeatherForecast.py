import json
import os

import requests

app_key = os.environ['JD_WEATHER_APP_KEY']

webHookServerUrl = os.environ['WEBHOOK_SERVER_URL']


def main_handler():
    nanshan = {
        'city_name': '南山',
        "city_id": '706',
        "city_node": '101280604'
    }
    nanshan_report = get_city_report(nanshan)

    nanshan_card = generator_card(nanshan_report)

    # 发送飞书卡片
    requests.post(webHookServerUrl, json=nanshan_card)


def generator_card(report):
    # 构造飞书卡片
    card = {
        "msg_type": 'interactive',
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": "blue",
                "title": {
                    "content": "🌤️ 深圳天气预报 🌤️",
                    "tag": "plain_text"

                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": f"城市:** {report['city_name']}**",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "content": f"日期:** {report['report_date']}**",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "content": f"天气状况:** {report['weather']}**",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "content": f"平均气温 **{report['temp']}**℃ 最低气温 **{report['temp_low']}**℃ 最高气温 **{report['temp_high']}**℃",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "fields": [],
                    "tag": "div"
                }
            ]
        }
    }
    # 组装指数建议,双数增加分割线
    for i in range(len(report['index'])):
        card['card']['elements'][6]['fields'].append({
            "is_short": True,
            "text": {
                "content": f"**{report['index'][i]['iname']}**:\n {report['index'][i]['detail']}",
                "tag": "lark_md"
            }
        })
    return card


def get_city_report(city):
    city_report = {
        "city_name": '',
        "report_date": '',
        "weather": '',
        "temp": '',
        "temp_low": '',
        "temp_high": '',
        "index": []
    }

    url = f'https://way.jd.com/jisuapi/weather?' \
          f'city=深圳&cityid={city["city_id"]}&citycode={city["city_node"]}&appkey={app_key}'

    response = requests.get(url)

    # 解析京东天气
    if response.status_code == 200:
        data = response.json()
        if data['code'] == '10000':
            result = data['result']['result']
            city_report['city_name'] = city['city_name']
            city_report['temp'] = result['temp']
            city_report['weather'] = result['weather']
            city_report['index'] = result['index']
            city_report['report_date'] = result['date'] + ' ' + result['week']
            city_report['temp_low'] = result['templow']
            city_report['temp_high'] = result['temphigh']
            city_report['temp'] = result['temp']
            return city_report
        else:
            print(data['msg'])


if __name__ == '__main__':
    push_weather_forecast()
