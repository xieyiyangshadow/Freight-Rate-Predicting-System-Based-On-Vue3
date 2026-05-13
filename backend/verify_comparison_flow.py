import io
import json
import time

import requests


BASE = 'http://127.0.0.1:8000'
USER = {"id": 2, "username": "ui_user_260509", "phone": "13800000099"}
HEADERS = {"X-Client-User": json.dumps(USER)}


def wait_for_completed(session, model_id, timeout=25):
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = session.get(f'{BASE}/api/models/{model_id}/', headers=HEADERS)
        data = response.json()
        if data.get('status') == 'completed':
            return data
        time.sleep(1)
    raise TimeoutError(f'model {model_id} did not complete in time')


def wait_for_prediction(session, task_id, timeout=25):
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = session.get(f'{BASE}/api/predictions/{task_id}/', headers=HEADERS)
        data = response.json()
        if data.get('status') == 'completed':
            return data
        time.sleep(1)
    raise TimeoutError(f'task {task_id} did not complete in time')


def main():
    session = requests.Session()

    create_model = session.post(
        f'{BASE}/api/models/',
        data={'name': '对比模型'},
        files={'file': ('comparison_model.bin', io.BytesIO(b'comparison model content'), 'application/octet-stream')},
        headers=HEADERS,
    )
    print('create model', create_model.status_code, create_model.text)
    new_model_id = create_model.json()['id']
    model_detail = wait_for_completed(session, new_model_id)
    print('new model detail', json.dumps(model_detail, ensure_ascii=False))

    create_task = session.post(
        f'{BASE}/api/predictions/',
        json={
            'name': '双模型对比任务',
            'origin': '北京',
            'destination': '深圳',
            'models_used': [4, new_model_id],
        },
        headers=HEADERS,
    )
    print('create task', create_task.status_code, create_task.text)
    task_id = create_task.json()['id']
    task_detail = wait_for_prediction(session, task_id)
    print('completed task detail', json.dumps(task_detail, ensure_ascii=False))


if __name__ == '__main__':
    main()
