import os

import requests
from bs4 import BeautifulSoup

webHookServerUrl = os.environ['WEBHOOK_SERVER_URL']


def main_handler():
    content = []
    # 爬取今日历史
    web_url = 'https://today.help.bj.cn/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(web_url, headers=headers)
    response.encoding = 'utf-8'
    # 向链接发送get请求获得页面
    soup = BeautifulSoup(response.text, 'html.parser')
    # 解析页面
    for i in range(len(soup.find_all('li', class_='typeid_0'))):
        if i == 0:
            continue
        content.append({
            # a连接的title
            'content': soup.find_all('li', class_='typeid_0')[i].find('a').get('title'),
            "year": soup.find_all('li', class_='typeid_0')[i].find('div', class_='cbp_tmicon').text
        })
    jsonStr = {
        "msg_type": 'interactive',
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "fields": [],
                    "tag": "div",
                }
            ],
            "header": {
                "template": "blue",
                "title": {
                    "content": "🎉 历史上的今天 🎉",
                    "tag": "plain_text",
                }
            }
        }
    }
    # 拼接
    for i in range(10):
        data = {
            "is_short": False,
            "text": {
                "content": "",
                "tag": "lark_md"
            },
        }
        # 加粗
        data['text']['content'] = f" {i + 1}.** {content[i]['year']}年 {content[i]['content']}**"
        jsonStr['card']['elements'][0]['fields'].append(data)

    r = requests.post(webHookServerUrl, json=jsonStr)
    print(r.text)
