import json
import random

import redis
from flask import Flask, jsonify, request

import configs

app = Flask(__name__)
configs = configs.configs

# 调试的时候使用, 解决跨域的问题
# from flask_cors import *
# CORS(app, supports_credentials=True)

r = redis.Redis(**configs['redis'])


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    res = {'code': 0, 'message': '', 'result': {'code': ''}}
    if request.method == 'POST':
        data = request.json
        if data is None or data['text'] is None or data['once'] is None:
            res['code'] = 1
            res['message'] = 'Text or Once is missed.'
        else:
            random_code = '%04d' % random.randint(0, 9999)
            while r.get(f'{random_code}_text') is not None:
                random_code = '%04d' % random.randint(0, 9999)
            r.set(f'{random_code}_text', data['text'], ex=3600)
            r.set(f'{random_code}_once', str(data['once']), ex=3600)
            res['result']['code'] = random_code
    else:
        res['code'] = 1
        res['message'] = 'Only Post request accepted.'
    return jsonify(res)


@app.route('/extract', methods=['GET', 'POST'])
def extract():
    res = {'code': 0, 'message': '', 'result': {'text': ''}}
    if request.method == 'POST':
        data = request.json
        if data is None or data['code'] is None:
            res['code'] = 1
            res['message'] = 'Code is missed.'
        else:
            code = data['code']
            if r.get(f'{code}_text') is None:
                res['code'] = 2
                res['message'] = 'Code dose not exsist.'
            else:
                text = r.get(f'{code}_text')
                once = r.get(f'{code}_once')
                if once == 'True':
                    r.delete(f'{code}_text')
                    r.delete(f'{code}_once')
                res['result']['text'] = text
    else:
        res['code'] = 1
        res['message'] = 'Only Post request accepted.'
    return jsonify(res)


if __name__ == '__main__':
    app.run()
