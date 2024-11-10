import os
import random

from flask import Flask, jsonify, request, send_file

import abs
import azredis
from werkzeug.utils import secure_filename

APP_DIR = os.path.dirname(__file__)
DIST_DIR = os.path.join(APP_DIR, "dist")
API_PREFIX = "/syncbackend"

app = Flask(__name__, static_url_path="", static_folder=DIST_DIR)

# 调试的时候使用, 解决跨域的问题
# from flask_cors import *
# CORS(app, supports_credentials=True)


@app.route("/")
def hello_world():
    entry = os.path.join(DIST_DIR, "index.html")
    print(entry)
    return send_file(entry)


@app.route(f"{API_PREFIX}/health", methods=["GET"])
def health():
    res = {"code": 0, "message": "App is running."}
    return jsonify(res)


@app.route(f"{API_PREFIX}/submit", methods=["GET", "POST"])
def submit():
    res = {"code": 0, "message": "", "result": {"code": ""}}
    if request.method == "POST":
        data = request.json
        if data is None or data["text"] is None or data["once"] is None:
            res["code"] = 1
            res["message"] = "Text or Once is missed."
        else:
            random_code = "%04d" % random.randint(0, 9999)
            while azredis.get(f"{random_code}_text") is not None:
                random_code = "%04d" % random.randint(0, 9999)
            azredis.set(f"{random_code}_text", data["text"])
            azredis.set(f"{random_code}_once", str(data["once"]))
            res["result"]["code"] = random_code
    else:
        res["code"] = 1
        res["message"] = "Only Post request accepted."
    return jsonify(res)


@app.route(f"{API_PREFIX}/extract", methods=["GET", "POST"])
def extract():
    res = {"code": 0, "message": "", "result": {"text": ""}}
    if request.method == "POST":
        data = request.json
        if data is None or data["code"] is None:
            res["code"] = 1
            res["message"] = "Code is missed."
        else:
            code = data["code"]
            if azredis.get(f"{code}_text") is None:
                res["code"] = 2
                res["message"] = "Code dose not exsist."
            else:
                text = azredis.get(f"{code}_text")
                once = azredis.get(f"{code}_once")
                if once == "True":
                    azredis.delete(f"{code}_text")
                    azredis.delete(f"{code}_once")
                res["result"]["text"] = text
    else:
        res["code"] = 1
        res["message"] = "Only Post request accepted."
    return jsonify(res)


@app.route(f"{API_PREFIX}/upload", methods=["GET", "POST"])
def uploader():
    res = {"code": 0, "message": "", "result": {"code": ""}}
    if request.method == "POST":
        try:
            file = request.files["file"]
            file_name = secure_filename(file.filename)

            random_code = "%04d" % random.randint(0, 9999)
            while azredis.get(f"{random_code}_file") is not None:
                random_code = "%04d" % random.randint(0, 9999)
            azredis.set(f"{random_code}_file", file_name)
            abs.upload(f"file-{random_code}", file.read())
            res["result"]["code"] = random_code
        except Exception as ex:
            res["code"] = 1
            res["message"] = str(ex)
    return jsonify(res)


@app.route(f"{API_PREFIX}/checkfile/<string:upload_code>", methods=["GET", "POST"])
def checkfile(upload_code: str):
    res = {"code": 0, "message": "", "result": {"filename": ""}}
    if not upload_code:
        res["code"] = 1
        res["message"] = "Code is missed."
    elif azredis.get(f"{upload_code}_file") is None:
        res["code"] = 2
        res["message"] = "Code dose not exsist."
    else:
        file_name = azredis.get(f"{upload_code}_file")
        res["result"]["filename"] = file_name
    return jsonify(res)


@app.route(f"{API_PREFIX}/download/<string:upload_code>", methods=["GET", "POST"])
def download(upload_code: str):
    res = {"code": 0, "message": "", "result": {"text": ""}}
    if not upload_code:
        res["code"] = 1
        res["message"] = "Code is missed."
        return jsonify(res)
    if azredis.get(f"{upload_code}_file") is None:
        res["code"] = 2
        res["message"] = "Code dose not exsist."
        return jsonify(res)
    file_name = azredis.get(f"{upload_code}_file")
    download_file = abs.download(f"file-{upload_code}")
    return send_file(download_file, download_name=file_name, as_attachment=True)


if __name__ == "__main__":
    app.run()
