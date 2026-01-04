# 前端

基于 Vue 3 + TypeScript + Vite + Element Plus

## 技术栈

- **Vue 3** - Composition API
- **TypeScript** - 类型安全
- **Vite** - 现代构建工具
- **Element Plus** - UI 组件库
- **VueUse** - 组合式 API 工具集
- **pnpm** - 高效包管理器

## 环境要求

- Node.js >= 18
- pnpm >= 9.0

## 安装 pnpm

```bash
npm install -g pnpm
```

## 开始

```bash
# 进入 frontend 目录
cd frontend

# 安装依赖
pnpm install
```

## 开发

```bash
# 启动开发服务器 (http://localhost:3000)
pnpm dev
```

开发时会自动代理 `/syncbackend` 请求到 `http://localhost:8000`，需同时启动后端。

## 构建

```bash
# 构建生产版本（输出到 ../backend/dist）
pnpm build

# 预览构建结果
pnpm preview

# 类型检查
pnpm type-check
```

## 更新依赖

```bash
# 交互式升级
pnpm up -i --latest

# 或直接升级所有
pnpm update --latest
```

## 项目结构

```
src/
├── api/              # API 服务层
│   └── index.ts
├── views/            # 页面组件
│   ├── SyncView.vue
│   ├── ExtractView.vue
│   ├── UploadView.vue
│   └── DownloadView.vue
├── App.vue           # 根组件
├── main.ts           # 应用入口
└── vite-env.d.ts     # 类型声明
```
