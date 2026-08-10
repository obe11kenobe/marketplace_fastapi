import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'
import { setUnauthorizedHandler } from './api'
import { notify } from './toast'
import './assets/main.css'

setUnauthorizedHandler(() => {
  notify('Сессия истекла, войдите заново', 'error')
  router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
})

createApp(App).use(router).mount('#app')
