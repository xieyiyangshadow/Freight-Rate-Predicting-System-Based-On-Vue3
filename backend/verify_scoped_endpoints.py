import json
import requests


def main():
    payload = {"id": 2, "username": "ui_user_260509", "phone": "13800000099"}
    headers = {"X-Client-User": json.dumps(payload)}
    session = requests.Session()

    for url in [
        'http://127.0.0.1:8000/api/models/',
        'http://127.0.0.1:8000/api/predictions/',
    ]:
        response = session.get(url, headers=headers)
        print(url, response.status_code)
        print(response.text)


if __name__ == '__main__':
    main()
