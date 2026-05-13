import requests
import json

BASE = 'http://127.0.0.1:8000'

def main():
    s = requests.Session()
    # register
    r = s.post(BASE + '/api/users/register/', json={'username':'testuser','phone':'13800000000','password':'pass123'})
    print('register', r.status_code, r.text)

    # login
    r = s.post(BASE + '/api/users/login/', json={'phone':'13800000000','password':'pass123'})
    print('login', r.status_code, r.text)

    # create model (json)
    r = s.post(BASE + '/api/models/', json={'owner':1,'name':'demo-model'})
    print('create model', r.status_code, r.text)

    # list models
    r = s.get(BASE + '/api/models/')
    print('list models', r.status_code, r.text)

    # upload a file with multipart to create another model
    with open('test_model.bin','wb') as f:
        f.write(b'dummy model content')
    with open('test_model.bin','rb') as mf:
        r = s.post(BASE + '/api/models/', data={'owner':1,'name':'uploaded-model'}, files={'file': mf})
    print('upload model', r.status_code, r.text)

    # create prediction (use model id 1)
    r = s.post(BASE + '/api/predictions/', json={'owner':1,'name':'task1','origin':'A','destination':'B','models_used':[1]})
    print('create prediction', r.status_code, r.text)

    # list predictions
    r = s.get(BASE + '/api/predictions/')
    print('list predictions', r.status_code, r.text)

if __name__ == '__main__':
    main()
