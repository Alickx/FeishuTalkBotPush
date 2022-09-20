import json
import os
import requests
from bs4 import BeautifulSoup


def push_weibo_hot_search():

    cookies = os.environ['WEIBO_COOKIE']
    webHookServerUrl = os.environ['WEBHOOK_SERVER_URL']

    news = []
    # 爬取微博热搜
    url = 'https://s.weibo.com/top/summary?cate=realtimehot'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }
    cookies = {i.split("=")[0]: i.split("=")[1] for i in cookies.split("; ")}
    response = requests.get(url, headers=headers, cookies=cookies)
    response.encoding = 'utf-8'
    # 向链接发送get请求获得页面
    soup = BeautifulSoup(response.text, 'html.parser')
    # 解析页面

    # 获取热搜标题和链接
    for i in soup.find_all('td', class_='td-02'):
        # 去除无用信息
        if i.find('a').get('href') != 'javascript:void(0);':
            news.append({
                'title': i.find('a').text,
                'url': 'https://s.weibo.com' + i.find('a').get('href'),
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
                    "content": "💪 微博热搜每日推送 💪",
                    "tag": "plain_text"
                }
            }
        }
    }

    # 拼接热搜
    for i in range(20):
        data = {
            "is_short": False,
            "text": {
                "content": "",
                "tag": "lark_md"
            },
        }
        # 加粗,makedown超链接格式：[链接文本](链接地址)
        data['text']['content'] = f" {i + 1}. [{news[i]['title']}]({news[i]['url']})"
        jsonStr['card']['elements'][0]['fields'].append(data)

    datajson = json.dumps(jsonStr, ensure_ascii=False)
    r = requests.post(webHookServerUrl, data=datajson.encode('utf-8'))
    print(r.text)


if __name__ == '__main__':
    push_weibo_hot_search()
