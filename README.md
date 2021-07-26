# Sync
一个简单的Web端文本同步工具。Motivation是为了解决在多平台下的文本同步的痛点，之前一直用OneNote作为同步工具，但是需要登录所以体验不够好，特别是在陌生设备上的时候。
[DEMO](https://app.cbdog94.cn/sync)

## 架构
[前端](frontend/README.md)使用的是Vue+element-ui，生成静态网页后部署到nginx上。[后端](backend/README.md)使用的是python3+flask，使用Gunicorn作为http服务器，同时使用nginx作为反向代理。

## 部署
1. 构建前端容器
2. 构建后端容器
3. 运行服务
    ```bash
    docker-compose up -d
    ```
## TODO
- 安全
- 优化代码
- 高并发
- 后端改成Java（练习）