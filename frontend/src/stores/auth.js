import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'
import api from '../api/client'

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
    const userData = {
      id: payload ? parseInt(payload.sub) : null,
      email: payload?.email || email,
      name: payload?.name || null,
      avatar: payload?.avatar || null,
      googleLinked: payload?.google_linked || false,
    }

    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
    return data
  }

  async function loginWithGoogle(googleToken) {
    try {
      const { data } = await api.post('/auth/google', {
        token: googleToken
      })

      _setTokens(data.access_token, data.refresh_token)

      const payload = _decodeJwt(data.access_token)
      const userData = {
        id: payload ? parseInt(payload.sub) : null,
        email: payload?.email || null,
        name: payload?.name || null,
        avatar: payload?.avatar || null,
        googleLinked: payload?.google_linked || false,
      }

      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
      return data
    } catch (error) {
      console.error('Google login error:', error)
      throw error
    }
  }

  async function linkGoogleAccount(googleToken) {
    try {
      const { data } = await authApi.linkGoogle(googleToken)
      _setTokens(data.access_token, data.refresh_token)

      const payload = _decodeJwt(data.access_token)
      user.value = {
        id: payload ? parseInt(payload.sub) : null,
        email: payload?.email || null,
        name: payload?.name || null,
        avatar: payload?.avatar || null,
        googleLinked: payload?.google_linked || false,
      }
      localStorage.setItem('user', JSON.stringify(user.value))
      return data
    } catch (error) {
      console.error('Помилка прив\'язки:', error)
      throw error
    }
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    // Одразу повертаємо користувача на сторінку входу
    window.location.href = '/'
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

  return { accessToken, refreshToken, user, isLoggedIn, register, login, loginWithGoogle, logout, linkGoogleAccount }
})