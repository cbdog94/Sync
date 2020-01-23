# 后端开发

基于flask+redis

## 环境


- 安装python3和redis


## 开始

 - 克隆或者下载当前仓库
 - 进入backend文件夹
 - 安装所需要的依赖

``` bash
pip3 install -r requirements.txt
```

## 开发

``` bash
FLASK_ENV=development python3 main.py --host=0.0.0.0
```

## 部属

``` bash
nohup gunicorn -w 4 -b 127.0.0.1:8000 main:app &
```

## 测试

``` bash
# 同步
$ curl -H "Content-Type:application/json" -X POST -d '{"text": "test", "once": true}' http://127.0.0.1:8000/submit

# 提取
$ curl -H "Content-Type:application/json" -X POST -d '{"code": "7918"}' http://127.0.0.1:8000/extract
```