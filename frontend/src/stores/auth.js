/**
 * @file Pinia store managing application-wide user authentication states, token lifecycles, and user profiles.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'
import api from '../api/client'

export const useAuthStore = defineStore('auth', () => {
  /** * Active Bearer authentication token.
   * @type {import('vue').Ref<string|null>} 
   */
  const accessToken = ref(localStorage.getItem('access_token') || null)

  /** * Long-lived token used to refresh the session.
   * @type {import('vue').Ref<string|null>} 
   */
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)

  /** * Active logged-in user profile details object.
   * @type {import('vue').Ref<Object|null>} 
   */
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  /** * Computed reactive state checker validating user status by access token presence.
   * @type {import('vue').ComputedRef<boolean>} 
   */
  const isLoggedIn = computed(() => !!accessToken.value)

  /**
   * Registers a user and logs them in immediately.
   * * @param {string} email - Profile target registration contact string.
   * @param {string} password - Master security authentication code text.
   * @param {string} name - Display identity label chosen by user.
   * @returns {Promise<Object>} Formatted object response structure.
   */
  async function register(email, password, name) {
    const { data } = await authApi.register({ email, password, name })
    await login(email, password)
    user.value = { ...user.value, name: data.name }
    localStorage.setItem('user', JSON.stringify(user.value))
    return data
  }

  /**
   * Standard Email/Password login processor that extracts and sets tokens.
   * * @param {string} email - Targeted authorization standard user identity email.
   * @param {string} password - Target security passcode passphrase text string.
   * @returns {Promise<Object>} Decoded network response body object block.
   */
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

  /**
   * Authenticates user records using external OAuth identity validation protocols with Google.
   * * @param {string} googleToken - Credential code string received from external Google SDK pipeline.
   * @returns {Promise<Object>} Handshake validation authentication endpoint response.
   */
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

  /**
   * Pairs an open standard profile container securely onto a Google target identity node.
   * * @param {string} googleToken - Validation hash key provided by Google account selection frameworks.
   * @returns {Promise<Object>} Handshake mapping update confirmation responses.
   */
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

  /**
   * Patches and alters core identity metadata parameters saved to active profiles.
   * * @param {Object} payload - Dynamic field tracking updates data structure mappings.
   * @returns {Promise<Object>} Network mutation confirmation payloads.
   */
  async function updateProfile(payload) {
    const { data } = await authApi.updateProfile(payload)
    _setTokens(data.access_token, data.refresh_token)

    const decoded = _decodeJwt(data.access_token)
    user.value = {
      ...user.value,
      name: decoded?.name || user.value.name,
      email: decoded?.email || user.value.email,
    }
    localStorage.setItem('user', JSON.stringify(user.value))
    return data
  }

  /**
   * Standard password reset interface router logic.
   * * @param {string} currentPassword - Existing string verification baseline credentials key.
   * @param {string} newPassword - Target secure configuration substitute code parameter.
   * @returns {Promise<Object>} Configuration change result status reports.
   */
  async function changePassword(currentPassword, newPassword) {
    const { data } = await authApi.changePassword({
      current_password: currentPassword,
      new_password: newPassword,
    })
    return data
  }

  /**
   * Resets reactive authentication states and purges local tracking tokens.
   */
  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    window.location.href = '/'
  }

  /**
   * Synchronizes operational cache definitions alongside long-term storage mechanisms.
   * * @private
   * @param {string} access - Initial token parameter authorizing environment requests.
   * @param {string} refresh - Backup validation token key re-authenticating sessions.
   */
  function _setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  /**
   * Breaks down standard base64 encrypted JWT hashes without contacting validation endpoints.
   * * @private
   * @param {string} token - Cryptographic security credential string.
   * @returns {Object|null} Extracted internal dictionary mapping payload records or null.
   */
  function _decodeJwt(token) {
    try {
      return JSON.parse(atob(token.split('.')[1]))
    } catch {
      return null
    }
  }

  return {
    accessToken, refreshToken, user, isLoggedIn,
    register, login, loginWithGoogle, logout, linkGoogleAccount,
    updateProfile, changePassword,
  }
})