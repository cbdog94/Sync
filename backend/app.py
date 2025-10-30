import os
import random

from flask import Flask, jsonify, request, send_file

import abs
import azsql
from werkzeug.utils import secure_filename
import time

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
    start_time = time.time()
    
    if request.method == "POST":
        data = request.json
        parse_time = time.time()
        print(f"Request parsing took {parse_time - start_time:.4f} seconds")
        
        if data is None or data["text"] is None or data["once"] is None:
            res["code"] = 1
            res["message"] = "Text or Once is missed."
        else:
            random_code = "%04d" % random.randint(0, 9999)
            
            # Check if code exists (azsql call)
            check_start = time.time()
            while azsql.get(f"{random_code}_text") is not None:
                random_code = "%04d" % random.randint(0, 9999)
            check_time = time.time()
            print(f"Code uniqueness check (azsql.get) took {check_time - check_start:.4f} seconds")
            
            # Store both text and once flag in a single batch operation
            set_start = time.time()
            azsql.set_many({
                f"{random_code}_text": data["text"],
                f"{random_code}_once": str(data["once"])
            })
            set_time = time.time()
            print(f"Storing text and once flag (azsql.set_many) took {set_time - set_start:.4f} seconds")
            
            res["result"]["code"] = random_code
            
            total_db_time = (check_time - check_start) + (set_time - set_start)
            print(f"Total azsql operations took {total_db_time:.4f} seconds")
    else:
        res["code"] = 1
        res["message"] = "Only Post request accepted."
    
    total_time = time.time() - start_time
    print(f"Total request processing took {total_time:.4f} seconds")

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
            # Batch get both text and once flag in a single operation
            results = azsql.get_many([f"{code}_text", f"{code}_once"])
            
            if f"{code}_text" not in results:
                res["code"] = 2
                res["message"] = "Code dose not exsist."
            else:
                text = results[f"{code}_text"]
                once = results.get(f"{code}_once")
                if once == "True":
                    # Batch delete both keys in a single operation
                    azsql.delete_many([f"{code}_text", f"{code}_once"])
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
            while azsql.get(f"{random_code}_file") is not None:
                random_code = "%04d" % random.randint(0, 9999)
            azsql.set(f"{random_code}_file", file_name)
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
    elif azsql.get(f"{upload_code}_file") is None:
        res["code"] = 2
        res["message"] = "Code dose not exsist."
    else:
        file_name = azsql.get(f"{upload_code}_file")
        res["result"]["filename"] = file_name
    return jsonify(res)


@app.route(f"{API_PREFIX}/download/<string:upload_code>", methods=["GET", "POST"])
def download(upload_code: str):
    res = {"code": 0, "message": "", "result": {"text": ""}}
    if not upload_code:
        res["code"] = 1
        res["message"] = "Code is missed."
        return jsonify(res)
    if azsql.get(f"{upload_code}_file") is None:
        res["code"] = 2
        res["message"] = "Code dose not exsist."
        return jsonify(res)
    file_name = azsql.get(f"{upload_code}_file")
    download_file = abs.download(f"file-{upload_code}")
    return send_file(download_file, download_name=file_name, as_attachment=True)


if __name__ == "__main__":
    app.run()
