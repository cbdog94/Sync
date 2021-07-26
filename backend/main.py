import random

import redis
from flask import Flask, jsonify, request, send_file

import configs
import abs
from werkzeug.utils import secure_filename

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


@app.route('/upload', methods=['GET', 'POST'])
def uploader():
    res = {'code': 0, 'message': '', 'result': {'code': ''}}
    if request.method == 'POST':
        try:
            file = request.files['file']
            file_name = secure_filename(file.filename)

            random_code = '%04d' % random.randint(0, 9999)
            while r.get(f'{random_code}_file') is not None:
                random_code = '%04d' % random.randint(0, 9999)
            r.set(f'{random_code}_file', file_name, ex=3600)

            abs.upload(f'file-{random_code}', file.read())

            res['result']['code'] = random_code
        except Exception as ex:
            res['code'] = 1
            res['message'] = str(ex)
    return jsonify(res)


@app.route('/checkfile/<string:upload_code>', methods=['GET', 'POST'])
def checkfile(upload_code: str):
    res = {'code': 0, 'message': '', 'result': {'filename': ''}}
    if not upload_code:
        res['code'] = 1
        res['message'] = 'Code is missed.'
    elif r.get(f'{upload_code}_file') is None:
        res['code'] = 2
        res['message'] = 'Code dose not exsist.'
    else:
        file_name = r.get(f'{upload_code}_file')
        res['result']['filename'] = file_name
    return jsonify(res)


@app.route('/download/<string:upload_code>', methods=['GET', 'POST'])
def download(upload_code: str):
    res = {'code': 0, 'message': '', 'result': {'text': ''}}
    if not upload_code:
        res['code'] = 1
        res['message'] = 'Code is missed.'
        return jsonify(res)
    if r.get(f'{upload_code}_file') is None:
        res['code'] = 2
        res['message'] = 'Code dose not exsist.'
        return jsonify(res)
    file_name = r.get(f'{upload_code}_file')
    download_file = abs.download(f'file-{upload_code}')
    return send_file(download_file, download_name=file_name, as_attachment=True)


if __name__ == '__main__':
    app.run()
