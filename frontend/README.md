# 前端开发

基于element-ui

## 环境

`Node >= 18`

- 安装node和yarn

``` bash
brew install node
npm install -g corepack
corepack enable
yarn set version berry
npm i -g npm-check-updates
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
ncu -u
yarn install
yarn up
```

## 开发

``` bash
# serve with hot reload at localhost:8010
yarn dev
# or npm run dev
```

## 部属
生成前端代码, 默认路径在backend/dist目录下
``` bash
# build for production with minification
yarn build
# or npm run build
```
~~构建docker image~~
``` bash
# deprecation 
# docker build -t sync_frontend .
```
