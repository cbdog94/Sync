import Vue from 'vue'
import Router from 'vue-router'
import ElementUI from 'element-ui'
// import 'element-ui/lib/theme-chalk/index.css'
import App from './App.vue'
const Sync = () => import('./Sync');
const Extract = () => import('./Extract');
import VueClipboard from 'vue-clipboard2'
import axios from 'axios'
import VueAxios from 'vue-axios'
 
Vue.use(VueAxios, axios)
Vue.use(VueClipboard)
Vue.use(Router)
Vue.use(ElementUI)


const router = new Router({
  routes :[
    { path: '/sync', component: Sync },
    { path: '/extract', component: Extract }
  ]
})

new Vue({
  el: '#app',
  router: router,
  render: h => h(App)
})
