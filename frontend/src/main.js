import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import App from './App.vue'
import VueClipboard from 'vue-clipboard2'
import axios from 'axios'
import VueAxios from 'vue-axios'

VueClipboard.config.autoSetContainer = true

const Sync = () => import('./Sync');
const Extract = () => import('./Extract');
const Upload = () => import('./Upload');
const Download = () => import('./Download');

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/sync', component: Sync },
    { path: '/extract', component: Extract },
    { path: '/upload', component: Upload },
    { path: '/download', component: Download }
  ]
})

const app = createApp(App)
  .use(VueAxios, axios)
  .use(VueClipboard)
  .use(router)
  .use(ElementPlus)
  .mount('#app')
