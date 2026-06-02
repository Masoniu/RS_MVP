import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'
import api from '../api/client'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  let refreshTimer = null

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
   _scheduleTokenRefresh()

   return data
}

  function logout() {
    if (refreshTimer) {
      clearTimeout(refreshTimer)
    }
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

  function _scheduleTokenRefresh() {
    if (refreshTimer) {
      clearTimeout(refreshTimer)
    }

    const token = accessToken.value
    if (!token) return

    const payload = _decodeJwt(token)
    if (!payload || !payload.exp) return

    const expiresAt = payload.exp * 1000
    const now = Date.now()
    const timeUntilExpiry = expiresAt - now

    const refreshBeforeExpiry = 60 * 1000
    const delayUntilRefresh = Math.max(timeUntilExpiry - refreshBeforeExpiry, 5000)

    refreshTimer = setTimeout(() => {
      _refreshAccessToken()
    }, delayUntilRefresh)
  }

  async function _refreshAccessToken() {
    if (!refreshToken.value) {
      logout()
      return
    }

    try {
      const { data } = await api.post('/auth/refresh', {
        refresh_token: refreshToken.value
      })

      _setTokens(data.access_token, data.refresh_token)

      _scheduleTokenRefresh()
     } catch (error) {
       logout()
     }
   }

   if (accessToken.value && refreshToken.value) {
     setTimeout(() => {
       _scheduleTokenRefresh()
     }, 100)
   }

  return { accessToken, refreshToken, user, isLoggedIn, register, login, logout }
})