import { createRouter, createWebHistory } from 'vue-router'
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import Lobby from './components/Lobby.vue'
import Room from './components/Room.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/lobby',
    name: 'Lobby',
    component: () => import('./components/Lobby.vue')
  },
  {
    path: '/room',
    name: 'Room',
    component: () => import('./components/Room.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router