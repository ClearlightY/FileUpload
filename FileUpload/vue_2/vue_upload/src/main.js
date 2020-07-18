import Vue from 'vue'
import App from './App.vue'
import uploader from 'vue-simple-uploader'
import components from './utils/components.js'
import Axios from 'axios'
import VueAxios from 'vue-axios'
import $ from 'jquery'
import './assets/upload-icon/iconfont.css'

Vue.prototype.$axios = Axios

Vue.config.productionTip = false

Vue.use(uploader)
Vue.use(components)
Vue.use(Axios)


new Vue({
  render: h => h(App),
}).$mount('#app')
