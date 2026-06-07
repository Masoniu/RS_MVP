import api from './client'
 
export const authApi = {
  register(payload) {
    return api.post('/auth/register', payload)
  },
 
  login({ email, password }) {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },

  loginWithGoogle(token) {
  return api.post('/auth/google', { token })
  }
}