/**
 * @file Application entry point file.
 * Initializes the root Vue instance, attaches core global plugins (Pinia, Router), 
 * and imports essential global stylesheets.
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router.js'

import 'bootstrap/dist/css/bootstrap.min.css'
import './style.css'

/**
 * @constant {Object} app - The core executable Vue application instance.
 */
const app = createApp(App)
/**
 * @constant {Object} pinia - The central state management store instance.
 */
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')