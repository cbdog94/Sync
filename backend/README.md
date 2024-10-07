# 后端开发

基于flask+redis

## 环境


- 安装python3


## 开始

 - 克隆或者下载当前仓库
 - 进入backend文件夹
 - 安装所需要的依赖

``` bash
pip3 install -r requirements.txt
```
- 进入frontend文件夹
- 根据对应README，生成前端网页
- 确保backend文件夹下有dist目录

## 开发
添加环境变量 AZURE_REDIS_HOST AZURE_STORAGE_ACCOUNT_URL
运行 flask
``` bash
az login
FLASK_ENV=development python3 app.py --host=0.0.0.0
```

## 部属

``` bash
nohup gunicorn -w 4 -b 127.0.0.1:8000 app:app &
```
构建docker image
``` bash
docker build -t sync_backend .
```

## 测试

``` bash
# 运行
docker run -d -p 8000:8000 --name test_sync sync_backend

# 同步
$ curl -H "Content-Type:application/json" -X POST -d '{"text": "test", "once": true}' http://127.0.0.1:8000/submit

# 提取
$ curl -H "Content-Type:application/json" -X POST -d '{"code": "7918"}' http://127.0.0.1:8000/extract
```

查看docker日志
``` bash
docker logs #Container ID#
```