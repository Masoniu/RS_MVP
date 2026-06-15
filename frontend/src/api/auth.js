/**
 * @file API module handling authentication-related network endpoints.
 */

import api from './client'

/**
 * An object mapping containing methods to interact with backend authentication services.
 * @namespace authApi
 */
export const authApi = {
  /**
   * Registers a new user account.
   * * @memberof authApi
   * @param {Object} payload - The user registration data.
   * @param {string} payload.email - The user's email address.
   * @param {string} payload.password - The user's password.
   * @param {string} payload.name - The user's display name.
   * @returns {Promise<AxiosResponse<any>>} The network response promise.
   */
  register(payload) {
    return api.post('/auth/register', payload)
  },

  /**
   * Logs in a user using standard Email/Password credentials.
   * Converts fields into an application/x-www-form-urlencoded format.
   * * @memberof authApi
   * @param {Object} credentials - The standard sign-in credentials.
   * @param {string} credentials.email - User email address matching OAuth username field.
   * @param {string} credentials.password - Plaintext security verification string.
   * @returns {Promise<AxiosResponse<any>>} The network response promise.
   */
  login({ email, password }) {
    /** @constant {URLSearchParams} form - The url-encoded form body parser. */
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    
    return api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },

  /**
   * Log into the system using a federated Google account credential token.
   * * @memberof authApi
   * @param {string} token - The Identity token supplied from Google Sign-In SDK.
   * @returns {Promise<AxiosResponse<any>>} The network response promise.
   */
  loginWithGoogle(token) {
    return api.post('/auth/google', { token })
  },

  /**
   * Links a Google identity account layer onto an existing authenticated standard profile.
   * * @memberof authApi
   * @param {string} token - The authorization credential string retrieved from Google.
   * @returns {Promise<AxiosResponse<any>>} The network response promise.
   */
  linkGoogle(token) {
    return api.post('/auth/link-google', { token })
  },

  /**
   * Modifies existing personal user details (e.g., updating user name or profile elements).
   * * @memberof authApi
   * @param {Object} payload - Partial profile updates.
   * @returns {Promise<AxiosResponse<any>>} The network response promise.
   */
  updateProfile(payload) {
    return api.patch('/auth/profile', payload)
  },

  /**
   * Authorizes a structural change to the user's password.
   * * @memberof authApi
   * @param {Object} payload - Password alteration collection block.
   * @param {string} payload.current_password - Validation check of active password string.
   * @param {string} payload.new_password - Target secure substitute password string.
   * @returns {Promise<AxiosResponse<any>>} The network response promise.
   */
  changePassword(payload) {
    return api.post('/auth/change-password', payload)
  },
}