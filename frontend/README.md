# 前端开发

基于element-ui

## 环境

`Node >= 6`

- 安装node和yarn

``` bash
brew install node
brew install yarn
```

## 开始

 - 克隆或者下载当前仓库
 - 进入frontend文件夹
 - 安装所需要的依赖

``` bash
yarn
```

## 更新依赖（非必须）
减少可能的安全隐患
``` bash
yarn upgrade
```

## 开发

``` bash
# serve with hot reload at localhost:8010
npm run dev
```

## 部属
生成前端代码
``` bash
# build for production with minification
npm run build
```
构建docker image
``` bash
docker build -t sync_frontend .
```
