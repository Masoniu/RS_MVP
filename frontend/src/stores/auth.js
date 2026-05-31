import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!accessToken.value)

  async function register(email, password, name) {
    const { data } = await authApi.register({ email, password, name })

    await login(email, password)
    user.value = { ...user.value, name: data.name }
    localStorage.setItem('user', JSON.stringify(user.value))
    return data
  }

  async function login(email, password) {
  const { data } = await authApi.login({ email, password })
  _setTokens(data.access_token, data.refresh_token)

  const payload = _decodeJwt(data.access_token)

  console.log("РОЗКОДОВАНИЙ ТОКЕН:", payload)
  
  const userData = {
    id: payload ? parseInt(payload.sub) : null,
    email: payload?.email || email,
    name: payload?.name || null, 
  }
  
  user.value = userData
  localStorage.setItem('user', JSON.stringify(userData))
  return data
}

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  function _setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function _decodeJwt(token) {
    try {
      return JSON.parse(atob(token.split('.')[1]))
    } catch {
      return null
    }
  }

  return { accessToken, refreshToken, user, isLoggedIn, register, login, logout }
})