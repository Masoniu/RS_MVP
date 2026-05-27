import { createRouter, createWebHistory } from 'vue-router'
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import { useAuthStore } from './stores/auth'

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
    path: '/room/:id',
    name: 'Room',
    component: () => import('./components/Room.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.name !== 'Login' && to.name !== 'Register' && !authStore.isLoggedIn) {
    next({ name: 'Login' })
  }
  else if ((to.name === 'Login' || to.name === 'Register') && authStore.isLoggedIn) {
    next({ name: 'Lobby' })
  }
  else {
    next()
  }
})

export default router