# Sync
一个简单的Web端文本同步工具。Motivation是为了解决在多平台下的文本同步的痛点，之前一直用OneNote作为同步工具，但是需要登录所以体验不够好，特别是在陌生设备上的时候。
[DEMO](https://sync.cbdog94.com)

## 架构
[前端](frontend/README.md)使用的是Vue+element-ui，生成静态网页后部署到backend。[后端](backend/README.md)使用的是python3+flask，使用Gunicorn作为http服务器。存储使用的是Azure提供的Azure Redis和Azure Blob Service。

## 部署
1. 线上通过Github Actions，持续部署到Azure App Service
2. 线下可通过Docker或者Gunicorn，运行服务