import json
import os
import requests
from requests_toolbelt import MultipartEncoder


def main_handler():
    webhook_url = os.environ['WEBHOOK_SERVER_URL']

    url = "https://api.bilibili.com/x/web-interface/popular?ps=20&pn=1"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    cookies = os.environ['BILIBILI_COOKIES']

    cookies = {i.split("=")[0]: i.split("=")[1] for i in cookies.split("; ")}

    response = requests.get(url, headers=headers, cookies=cookies)

    # 获取B站热门视频标题和链接
    news = []
    j = 0
    for i in response.json()['data']['list']:
        video_url = i['short_link']
        video_title = i['title']
        video_author = i['owner']['name']
        video_author_mid = i['owner']['mid']
        video_play = i['stat']['view']
        video_comment = i['stat']['danmaku']
        video_pic = i['pic']
        news.append({
            'video_url': video_url,
            'video_title': video_title,
            'video_author': video_author,
            'video_author_mid': 'https://space.bilibili.com/' + str(video_author_mid),
            'video_play': format_num(video_play),
            'video_comment': format_num(video_comment),
            'video_pic': video_pic
        })
        j += 1
        if j == 5:
            break

    jsonstr = feishu_card(news)

    print(json.dumps(jsonstr, ensure_ascii=False))

    requests.post(webhook_url, json=jsonstr)


def format_num(num):
    if num > 10000:
        return str(num // 10000) + '万'
    else:
        return str(num)


def upload_img(image_url):
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    # 下载图片
    img = requests.get(image_url).content
    form = {'image_type': 'message',
            'image': (f'{image_url.split("/")[-1]}', img, 'image/jpeg')}
    multi_form = MultipartEncoder(form)
    token = get_token()
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': multi_form.content_type}
    response = requests.request("POST", url, headers=headers, data=multi_form)
    res = bytes.decode(response.content)
    res = eval(res)
    return res['data']['image_key']


def get_token():
    feishu_app_id = os.environ['FEISHU_APP_ID']
    feishu_app_secret = os.environ['FEISHU_APP_SECRET']

    url = f'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal?app_id={feishu_app_id}&app_secret={feishu_app_secret}'
    res = requests.get(url=url)
    token = res.json()
    token_text = token['tenant_access_token']
    return token_text


def feishu_card(news):
    # 组装飞书卡片
    jsonStr = {
        "msg_type": 'interactive',
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [],
            "header": {
                "template": "blue",
                "title": {
                    "content": "💪 BiliBili热门视频定时推送 💪",
                    "tag": "plain_text"
                }
            }
        }
    }

    for i in news:
        jsonStr['card']['elements'].append({
            "tag": "div",
            "text": {
                "content": f"🔥 {i['video_title']}",
                "tag": "lark_md"
            }
        })
        jsonStr['card']['elements'].append({
            "tag": "img",
            "img_key": upload_img(i['video_pic']),
            "alt": {
                "content": "图片"
            }
        })
        jsonStr['card']['elements'].append({
            "tag": "div",
            "fields": [
                {
                    "is_short": True,
                    "text": {
                        "content": f"👤 作者：[{i['video_author']}]({i['video_author_mid']})",
                        "tag": "lark_md"
                    }
                },
                {
                    "is_short": True,
                    "text": {
                        "content": f"👉 链接：{i['video_url']}",
                        "tag": "lark_md"
                    }
                },
                {
                    "is_short": True,
                    "text": {
                        "content": f"👁️ 播放：{i['video_play']}",
                        "tag": "lark_md"
                    }
                },
                {
                    "is_short": True,
                    "text": {
                        "content": f"💬 评论：{i['video_comment']}",
                        "tag": "lark_md"
                    }
                }
            ]
        })
        # hr
        if i != news[-1]:
            jsonStr['card']['elements'].append({
                "tag": "hr"
            })

    return jsonStr


if __name__ == '__main__':
    main_handler()
