import io
import json
import time
from pathlib import Path

import requests


BASE = 'http://127.0.0.1:8000'
USER = {"id": 2, "username": "ui_user_260509", "phone": "13800000099"}
HEADERS = {"X-Client-User": json.dumps(USER)}


def wait_until_completed(session, url, timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = session.get(url, headers=HEADERS)
        data = response.json()
        if data.get('status') == 'completed':
            return data
        time.sleep(1)
    raise TimeoutError(f'timeout waiting for {url}')


def wait_for_task(session, task_id, timeout=20):
    return wait_until_completed(session, f'{BASE}/api/predictions/{task_id}/', timeout=timeout)


def main():
    session = requests.Session()
    payload = {
        'name': '业务验证模型',
    }
    files = {
        'file': ('demo_model.bin', io.BytesIO(b'business test model content'), 'application/octet-stream')
    }
    create_model = session.post(f'{BASE}/api/models/', data=payload, files=files, headers=HEADERS)
    print('create model', create_model.status_code, create_model.text)
    model_id = create_model.json()['id']

    model_detail = wait_until_completed(session, f'{BASE}/api/models/{model_id}/')
    print('completed model detail', json.dumps(model_detail, ensure_ascii=False))

    task_payload = {
        'name': '业务验证任务',
        'origin': '上海',
        'destination': '广州',
        'models_used': [model_id],
    }
    create_task = session.post(f'{BASE}/api/predictions/', json=task_payload, headers=HEADERS)
    print('create task', create_task.status_code, create_task.text)
    task_id = create_task.json()['id']

    task_detail = wait_for_task(session, task_id)
    print('completed task detail', json.dumps(task_detail, ensure_ascii=False))

    print('scoped models', session.get(f'{BASE}/api/models/', headers=HEADERS).text)
    print('scoped tasks', session.get(f'{BASE}/api/predictions/', headers=HEADERS).text)


if __name__ == '__main__':
    main()
