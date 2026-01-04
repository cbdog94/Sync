import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import { api } from './api'

// 路由懒加载
const routes = [
  { path: '/', redirect: '/sync' },
  { path: '/sync', component: () => import('./views/SyncView.vue') },
  { path: '/extract', component: () => import('./views/ExtractView.vue') },
  { path: '/upload', component: () => import('./views/UploadView.vue') },
  { path: '/download', component: () => import('./views/DownloadView.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局提供 API
app.provide('api', api)

app.use(router)
app.use(ElementPlus)
app.mount('#app')
