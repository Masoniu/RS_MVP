/**
 * @file Core Axios client orchestration engine containing token interceptors, 
 * token automatic refresh structures, and global application server sleep loaders.
 */

import axios from 'axios'
import { ref } from 'vue'

/**
 * Global reactive indicator reflecting if an environment instance is undergoing cold startup.
 * @type {import('vue').Ref<boolean>}
 */
export const isServerWakingUp = ref(false)

/**
 * @constant {AxiosInstance} api - Dedicated modular standard Axios configuration framework setup.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json' },
})

/** * Tracking variable counting ongoing asynchronous HTTP operations.
 * @type {number} 
 */
let activeRequests = 0;

/** * Timeout reference tracking cold-start server-wake delays.
 * @type {null|ReturnType<typeof setTimeout>} 
 */
let wakingUpTimeout = null;

/** * Request Interceptor pipeline setting Authorization Bearer tokens.
 */
api.interceptors.request.use((config) => {
  /** @constant {string|null} token - Retreived persistent access payload string. */
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/** * Boolean flag preventing racing execution of overlapping refresh token invocations.
 * @type {boolean} 
 */
let isRefreshing = false

/** * Staging array queue caching unexecuted network queries while a token renewal pipeline processes.
 * @type {Array<{resolve: Function, reject: Function}>} 
 */
let failedQueue = []

/**
 * Iterates through cached queue queries executing pending requests post-refresh token extraction.
 * * @param {Error|null} error - The validation error object if the refresh operation failed.
 * @param {string|null} [token=null] - The newly initialized Access Token payload string.
 */
function processQueue(error, token = null) {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

/**
 * Decrements the count of active network queries and turns off the server-waking overlay when requests hit zero.
 */
function stopLoader() {
  activeRequests--;
  if (activeRequests <= 0) {
    activeRequests = 0;
    clearTimeout(wakingUpTimeout);
    isServerWakingUp.value = false;
  }
}

/**
 * Response interceptor mapping network completions or orchestrating 401 token refreshes.
 */
api.interceptors.response.use(
  (response) => {
    stopLoader();
    return response;
  },
  async (error) => {
    stopLoader();

    /** @constant {InternalAxiosRequestConfig} originalRequest - The original configuration context metadata. */
    const originalRequest = error.config

    // Catch unauthorized status codes (401) and prevent cyclical infinite loops via custom flag
    if (error.response?.status === 401 && !originalRequest._retry) {
      
      // If a token refresh process is already active, push request promise to queue
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      /** @constant {string|null} refreshToken - Stored long-lived profile update hash key string. */
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        _logout()
        return Promise.reject(error)
      }

      try {
        /** @constant {Object} response - Isolated renewal server request response body. */
        const { data } = await axios.post(
            `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/auth/refresh`,
            { refresh_token: refreshToken },
        )
        
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        
        api.defaults.headers.common.Authorization = `Bearer ${data.access_token}`
        
        processQueue(null, data.access_token)
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        _logout()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  },
)

/**
 * Utility method purging system storage data keys and forcing layout re-routing to standard root view.
 * @private
 */
function _logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  window.location.href = '/'
}

export default api