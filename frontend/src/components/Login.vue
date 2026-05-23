<template>
  <div class="login-page d-flex align-items-center justify-content-center">
    <div class="container px-4 text-center">

      <div class="glass-card mx-auto">
        
        <div class="mb-4">
          <img src="../assets/logo.svg" alt="RouteSplitter Logo" class="logo-image mx-auto mb-3 d-block">
          <h1 class="fw-bold mb-2 main-title">RouteSplitter</h1>
          <p class="subtitle mx-auto">Твій персональний помічник<br>у плануванні прогулянок!</p>
        </div>

        <form @submit.prevent="handleLogin" class="auth-form mx-auto">

          <div class="mb-3 text-start">
            <label class="form-label ms-1 custom-label">E-mail</label>
            <input v-model="email" type="email" class="form-control pretty-input" placeholder="example@mail.com">
          </div>

          <div class="mb-4 text-start">
            <label class="form-label ms-1 custom-label">Пароль</label>
            <input v-model="password" type="password" class="form-control pretty-input" placeholder="••••••••">
          </div>

          <button class="btn btn-primary w-100 rounded-pill brown-btn mb-4">Увійти</button>

          <div class="divider mb-4">
            <span>або</span>
          </div>

          <button class="btn w-100 rounded-pill google-btn mb-4 d-flex align-items-center justify-content-center">
            <svg class="google-icon me-2" viewBox="0 0 488 512"><path d="M488 261.8C488 403.3 391.1 504 248 504 110.8 504 0 393.2 0 256S110.8 8 248 8c66.8 0 123 24.5 166.3 64.9l-67.5 64.9C258.5 52.6 94.3 116.6 94.3 256c0 86.5 69.1 156.6 153.7 156.6 98.2 0 135-70.4 140.8-106.9H248v-85.3h236.1c2.3 12.7 3.9 24.9 3.9 41.4z"/></svg>
            Продовжити з Google
          </button>

        </form>

        <p class="bottom-text mb-0">
          Немає акаунту? <a href="#" class="register-link">Зареєструватись</a>
        </p>

      </div>
      </div>
  </div>
</template>

<script setup>
import { ref } from 'vue' 
import { useRouter } from 'vue-router' 
import { useAuthStore } from '../stores/auth'

const router = useRouter() 
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')
 
async function handleLogin() {
  loading.value = true
  errorMsg.value = ''
  try {
    await auth.login(email.value, password.value)
    router.push({ name: 'Lobby' })
  } catch (e) {
    errorMsg.value = e?.response?.data?.detail || 'Помилка входу. Перевірте email і пароль.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  padding: 20px 0;
}

.glass-card {
  max-width: 400px;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 24px;
  padding: 40px 20px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
}

.logo-image {
  width: auto;
  height: 100px;
}

.main-title {
  color: var(--color-primary);
  font-size: 26px;
}

.subtitle {
  font-size: 14px;
  line-height: 1.4;
  color: #625050;
  max-width: 250px;
}

.auth-form {
  max-width: 320px;
}

.custom-label {
  font-weight: 500;
  color: #625050;
}

.pretty-input {
  background-color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(98, 80, 80, 0.3);
  border-radius: 12px;
  height: 48px;
  padding: 10px 15px;
  transition: all 0.3s ease;
}

.pretty-input:focus {
  outline: none;
  background-color: #ffffff;
  border-color: var(--color-input-focus);
  box-shadow: 0 0 0 2px rgba(41, 44, 165, 0.15);
}

.brown-btn {
  background-color: #625050;
  color: #ffffff;
  border: none;
  height: 48px;
  border-radius: 12px !important;
  font-weight: 600;
  transition: all 0.3s ease;
}

.brown-btn:hover {
  background-color: #4a3c3c;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(98, 80, 80, 0.3);
}

.brown-btn:active {
  background-color: #4a3c3c;
  transform: translateY(1px);
  box-shadow: 0 2px 4px rgba(98, 80, 80, 0.3);
}

.google-btn {
  background-color: rgba(255, 255, 255, 0.8);
  color: #625050;
  border: 1px solid rgba(98, 80, 80, 0.3);
  height: 48px;
  border-radius: 12px !important;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
}

.google-btn:hover {
  background-color: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.google-btn:active {
  background-color: #ffffff;
  transform: translateY(1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.google-icon {
  width: 18px;
  height: 18px;
  fill: #625050;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #625050;
  opacity: 0.6;
}

.divider::before, .divider::after {
  content: "";
  flex: 1;
  border-bottom: 1px solid #625050;
}

.divider span {
  padding: 0 15px;
  font-size: 14px;
}

.bottom-text {
  font-size: 14px;
  color: #625050;
}

.register-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
}
</style>