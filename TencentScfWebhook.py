import os
import requests


def main_handler(event, context):
    token = os.environ.get('TOKEN')
    # 远程github action webhook
    webhook_url = os.environ.get('WEBHOOK_URL')
    event_type = os.environ.get('EVENT_TYPE')

    headers = {
        'Authorization': 'token ' + token,
    }

    json = {
        'event_type': event_type,
    }

    requests.post(webhook_url, headers=headers, json=json)
    print('今日飞书推送已完成')

