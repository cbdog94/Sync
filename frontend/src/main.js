import Vue from 'vue'
import Router from 'vue-router'
import ElementUI from 'element-ui'
// import 'element-ui/lib/theme-chalk/index.css'
import App from './App.vue'
import VueClipboard from 'vue-clipboard2'
import axios from 'axios'
import VueAxios from 'vue-axios'

VueClipboard.config.autoSetContainer = true
Vue.use(VueAxios, axios)
Vue.use(VueClipboard)
Vue.use(Router)
Vue.use(ElementUI)

const Sync = () => import('./Sync');
const Extract = () => import('./Extract');
const Upload = () => import('./Upload');
const Download = () => import('./Download');

const router = new Router({
  routes: [
    { path: '/sync', component: Sync },
    { path: '/extract', component: Extract },
    { path: '/upload', component: Upload },
    { path: '/download', component: Download }
  ]
})

new Vue({
  el: '#app',
  router: router,
  render: h => h(App)
})
