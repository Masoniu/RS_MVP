/**
 * @file Application router configuration file (Vue Router).
 * Manages view mappings and implements navigation guard authorization rules.
 */
import { createRouter, createWebHistory } from 'vue-router'
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import { useAuthStore } from './stores/auth'

/**
 * @constant {Array<Object>} routes - Definition map array of application routes.
 * Employs static imports for auth views and lazy-loading imports for interior dashboard views.
 */
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
  },
  {
    path: '/create-room',
    name: 'CreatingRoom',
    component: () => import('./components/CreatingRoom.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('./components/Profile.vue')
  }
]

/**
 * @constant {Object} router - Configured router instance operating with native HTML5 History API.
 */
const router = createRouter({
  history: createWebHistory(),
  routes
})

/**
 * Global Navigation Guard.
 * Evaluates user authentication state prior to executing any routing transitions.
 * 
 * @function beforeEach
 * @param {Object} to - The target Route Object being navigated to.
 * @param {Object} from - The previous Route Object being navigated away from.
 * @param {Function} next - The callback function triggered to resolve, abort, or redirect navigation.
 */
router.beforeEach((to, from, next) => {
  /**
   * @constant {Object} authStore - Instance of Pinia authorization store used to check user state.
   */
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