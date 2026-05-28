<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const name = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const isSubmitted = ref(false);
const errorMessage = ref('');

const handleRegister = async () => {
  isSubmitted.value = true;
  errorMessage.value = '';

  if (!name.value || !email.value || !password.value || !confirmPassword.value) {
    return;
  }
  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Паролі не збігаються';
    return;
  }

  try {
    await authStore.register(email.value, password.value, name.value);
    await authStore.login(email.value, password.value);

    router.push('/lobby');
  } catch (error) {
    console.error(error);
    errorMessage.value = error.response?.data?.detail || 'Помилка під час реєстрації';
  }
};
</script>

<template>
  <div class="login-page d-flex align-items-center justify-content-center">
    <div class="container-fluid p-0 h-100">
      
      <div class="row g-0 h-100 min-vh-100">
        
        <div class="col-md-6 align-items-center justify-content-center route-visualization p-5">
          <div class="animation-container text-center">
            
            <svg viewBox="0 0 500 400" class="map-animation mb-4" xmlns="http://www.w3.org/2000/svg">
              <circle class="point p1" cx="80" cy="320" r="10" fill="#625050" />
              <circle class="point p2" cx="250" cy="120" r="10" fill="#625050" />
              <circle class="point p3" cx="420" cy="280" r="10" fill="#625050" />
              <path class="route-line" d="M80 320 L250 120 L420 280" stroke="#625050" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>

            <h2 class="fw-bold text-white mb-2 animation-title">Плануй. Розділяй. Кайфуй.</h2>
            <p class="text-white-50 animation-subtitle mx-auto">Твій маршрут та витрати під контролем.</p>
          </div>
        </div>

        <div class="col-md-6 d-flex align-items-center justify-content-center p-4 p-lg-5 forms-section">
          
          <div class="glass-card mx-auto">
            <div class="mb-4 text-center">
                <img src="../assets/logo.svg" alt="RouteSplitter Logo" class="logo-image mx-auto d-block">
  
                <div class="mobile-only-text mt-2 d-md-none">
                    <h1 class="fw-bold mb-1 main-title">RouteSplitter</h1>
                    <p class="subtitle mx-auto mb-0">Твій помічник у плануванні прогулянок!</p>
                </div>
            </div>

            <form @submit.prevent class="auth-form mx-auto">

              <div class="mb-3 text-start">
                <label class="form-label ms-1 custom-label">Ім'я</label>
                <input v-model="name" type="text" :class="{'error-glow': isSubmitted && !name}" class="form-control pretty-input">
              </div>

              <div class="mb-3 text-start">
                <label class="form-label ms-1 custom-label">E-mail</label>
                <input v-model="email" type="email" :class="{'error-glow': isSubmitted && !email}" class="form-control pretty-input" placeholder="example@mail.com">
              </div>

              <div class="mb-3 text-start">
                <label class="form-label ms-1 custom-label">Пароль</label>
                <input v-model="password" type="password" :class="{'error-glow': isSubmitted && !password}" class="form-control pretty-input" placeholder="••••••••">
              </div>

              <div class="mb-3 text-start">
                <label class="form-label ms-1 custom-label">Підтвердження пароля</label>
                <input v-model="confirmPassword" type="password" :class="{'error-glow': isSubmitted && !confirmPassword}" class="form-control pretty-input" placeholder="••••••••">
              </div>

              <div style="min-height: 45px; margin-bottom: 15px;">
                <div v-if="errorMessage" class="alert alert-danger py-2 text-center m-0" style="border-radius: 12px; font-size: 14px;">
                    {{ errorMessage }}
                </div>
            </div>

              <button @click="handleRegister" class="btn w-100 brown-btn mb-4 mt-2">Реєстрація
              </button>

              <div class="divider mb-4">
                <span>або</span>
              </div>

              <button class="btn w-100 google-btn mb-4 d-flex align-items-center justify-content-center">
                <svg class="google-icon me-2" viewBox="0 0 488 512"><path d="M488 261.8C488 403.3 391.1 504 248 504 110.8 504 0 393.2 0 256S110.8 8 248 8c66.8 0 123 24.5 166.3 64.9l-67.5 64.9C258.5 52.6 94.3 116.6 94.3 256c0 86.5 69.1 156.6 153.7 156.6 98.2 0 135-70.4 140.8-106.9H248v-85.3h236.1c2.3 12.7 3.9 24.9 3.9 41.4z"/></svg>
                Продовжити з Google
              </button>
            </form>

            <p class="bottom-text mb-0 text-center">
              Вже є акаунт? <router-link to="/" class="login-link">Увійти</router-link>
            </p>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.error-glow {
  border-color: #625050 !important;
  background-color: rgba(255, 152, 0, 0.05) !important;
  box-shadow: 0 0 0 3px rgba(255, 152, 0, 0.2) !important;
}

.login-page {
  min-height: 100vh;
  width: 100%;
}

.route-visualization {
  display: none;
}

.map-animation {
  width: 100%;
  max-width: 450px;
  height: auto;
}

.point {
  fill: #625050;
  opacity: 0;
  transform-origin: center;
  animation: appearPoint 0.5s ease forwards;
}

.p1 {
  animation-delay: 0.5s; 
}

.p2 {
  fill: #625050;
  animation-delay: 1.5s; 
}

.p3 {
  animation-delay: 2.5s; 
}

.route-line {
  stroke-dasharray: 500;
  stroke-dashoffset: 500;
  animation: drawRoute 2s linear forwards;
  animation-delay: 1.5s;
}

.animation-title {
  font-size: 32px;
}
.animation-subtitle {
  font-size: 16px;
  max-width: 300px;
}

@keyframes appearPoint {
  0% { opacity: 0; transform: scale(0); }
  70% { transform: scale(1.2); }
  100% { opacity: 1; transform: scale(1); }
}

@keyframes drawRoute {
  to { stroke-dashoffset: 0; }
}

.forms-section {
  background-color: var(--bg-main);
  background-image: 
    radial-gradient(circle at 80% 20%, rgba(98, 80, 80, 0.4) 0%, rgba(98, 80, 80, 0) 40%),
    radial-gradient(circle at 20% 80%, rgba(100, 109, 210, 0.5) 0%, rgba(100, 109, 210, 0) 45%);
}

.glass-card {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 24px;
  padding: 30px 20px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
  transition: transform 0.3s ease;
}

.logo-image {
  height: 85px; 
  margin-bottom: 10px;
}

.main-title {
  color: var(--color-primary); 
  font-size: 22px; 
  margin-bottom: 4px !important; 
}

.subtitle {
  font-size: 13px; 
  line-height: 1.4; 
  color: #625050; 
  max-width: 250px; 
}

.auth-form {
  max-width: 320px; 
}

.custom-label {
  font-weight: 500; color: #625050; 
}

.pretty-input {
  background-color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(98, 80, 80, 0.3);
  border-radius: 12px;
  height: 42px;
  transition: all 0.3s ease;
}

.pretty-input:focus {
  background-color: #ffffff;
  border-color: var(--color-input-focus);
  box-shadow: 0 0 0 2px rgba(41, 44, 165, 0.15);
}

.brown-btn {
  background-color: #625050;
  color: #ffffff;
  border: none;
  height: 42px;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.brown-btn:hover {
  background-color: #4a3c3c; 
  transform: translateY(-2px); 
}

.brown-btn:active {
  transform: translateY(1px); 
}

.google-btn {
  background-color: rgba(255, 255, 255, 0.8);
  color: #625050;
  border: 1px solid rgba(98, 80, 80, 0.3);
  height: 42px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.google-btn:hover { 
  background-color: #ffffff; 
  transform: translateY(-2px); 
}

.google-btn:active { 
  transform: translateY(1px); 
}

.google-icon { 
  width: 18px;
  height: 18px;
  fill: #625050; 
}

.divider {
  display: flex;
  align-items: center;
  color: #625050; 
  opacity: 0.6; 
  margin-bottom: 15px !important;
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

.login-link {
   color: var(--color-primary); 
   text-decoration: none; 
   font-weight: 600; 
}

@media (min-width: 767px) {

  .route-visualization {
    display: flex;
    position: relative;
    background: linear-gradient(135deg, rgba(41, 44, 165, 0.6) 0%, rgba(26, 28, 106, 0.6) 100%), 
                url('../assets/map.jpg');
    background-size: cover;
    background-position: center;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
  }

  .route-visualization::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(41, 44, 165, 0.2);
    z-index: 1;
  }

  .animation-container {
    position: relative;
    z-index: 2;
  }
}
</style>