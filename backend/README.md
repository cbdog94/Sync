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
