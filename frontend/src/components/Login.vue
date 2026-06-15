<script setup>
/**
 * @file Login.vue
 * @description Frontend login view component. Manages user authentication
 * using standard Email/Password input forms or federated Google Sign-In Identity APIs.
 */

import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

/**
 * Core application router engine driver used for view transitions.
 * @constant {Object} router
 */
const router = useRouter();

/**
 * Central identity profile authentication store context.
 * @constant {Object} authStore
 */
const authStore = useAuthStore();

/**
 * Bound reactive textual field capturing the user's input email address.
 * @type {import('vue').Ref<string>}
 */
const email = ref('');

/**
 * Bound reactive textual field capturing the user's secret password string.
 * @type {import('vue').Ref<string>}
 */
const password = ref('');

/**
 * Validation tracking flag indicating whether the login button has been clicked.
 * Used to display red warning borders or validation messages.
 * @type {import('vue').Ref<boolean>}
 */
const isSubmitted = ref(false);

/**
 * Text message body holding error details caught during form validation or network requests.
 * @type {import('vue').Ref<string>}
 */
const errorMessage = ref('');

/**
 * Loading state indicator for the Google Sign-In process. 
 * Disables buttons and shows spinning wheel indicators when true.
 * @type {import('vue').Ref<boolean>}
 */
const googleLoading = ref(false);

/**
 * Loading state indicator for the standard Email/Password authentication request.
 * @type {import('vue').Ref<boolean>}
 */
const isLoading = ref(false);

/**
 * The unique Google API Credentials Client ID fetched from environment variables.
 * @constant {string|undefined} GOOGLE_CLIENT_ID
 */
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

/**
 * Validates credentials and attempts a standard Email/Password login.
 * On success, routes the user directly to the application Lobby dashboard.
 * * @async
 * @function handleLogin
 * @returns {Promise<void>} Resolves once validation checks finish or routing completes.
 */
const handleLogin = async () => {
  isSubmitted.value = true;
  errorMessage.value = '';

  // Simple validation check: exit early if fields are completely blank
  if (!email.value || !password.value) {
    return;
  }

  isLoading.value = true;
  try {
    // Send form data to the central Pinia store authentication logic
    await authStore.login(email.value, password.value);
    router.push('/lobby');
  } catch (error) {
    console.error(error);
    errorMessage.value = error.response?.data?.detail || 'Невірний email або пароль';
  } finally {
    isLoading.value = false;
  }
};

/**
 * Processes the secure ID token returned from Google's native popup framework.
 * Passes the credential string to the backend to authenticate or log in the user.
 * * @async
 * @function handleGoogleLogin
 * @param {Object} response - The raw credential response object emitted by the Google API.
 * @param {string} response.credential - The secure JSON Web Token (JWT) provided by Google.
 * @returns {Promise<void>} Resolves when the social login handshake completes.
 */
const handleGoogleLogin = async (response) => {
  googleLoading.value = true;
  errorMessage.value = '';

  try {
    const { credential } = response;
    // Authenticate with backend using the Google token string
    await authStore.loginWithGoogle(credential);
    router.push('/lobby');
  } catch (error) {
    console.error('Google login error:', error);
    errorMessage.value = error.response?.data?.detail || 'Помилка при вході через Google';
  } finally {
    googleLoading.value = false;
  }
};

/**
 * Vue layout mounting listener. 
 * Automatically initializes Google's Identity services and renders the official 
 * visual Google Sign-In branding button once the DOM tree has successfully loaded.
 */
onMounted(() => {
  // Ensure both the global script window.google and your Client ID token exist before configuring
  if (window.google && GOOGLE_CLIENT_ID) {
    // 1. Initialize the Google JavaScript identity client framework library instance
    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: handleGoogleLogin, // Assigns target interceptor method for response handles
    });
    
    // 2. Render the custom styled Google Button inside the container targeting matching IDs
    window.google.accounts.id.renderButton(
      document.getElementById('google-button-container'),
      { theme: 'outline', size: 'large', width: '320' }
    );
  }
});
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

            <h2 class="fw-bold text-white mb-3 animation-title">Плануй. Розділяй. Кайфуй.</h2>
            <p class="text-white-50 animation-subtitle mx-auto">Твій маршрут та витрати під контролем.</p>
          </div>
        </div>

        <div class="col-md-6 d-flex align-items-center justify-content-center p-4 p-lg-5 forms-section">
          <div class="glass-card mx-auto">
            <div class="mb-4 text-center">
              <img src="../assets/logo.svg" alt="RouteSplitter Logo" class="logo-image mx-auto mb-3 d-block">
              <h1 class="fw-bold mb-2 main-title">RouteSplitter</h1>
              <p class="subtitle mx-auto">Твій помічник у плануванні прогулянок!</p>
            </div>

            <form @submit.prevent="handleLogin" class="auth-form mx-auto">

              <div class="mb-3 text-start">
                <label class="form-label ms-1 custom-label">E-mail</label>
                <input v-model="email" type="email" :class="{'error-glow': isSubmitted && !email}" class="form-control pretty-input" placeholder="example@mail.com">
              </div>
              <div class="mb-4 text-start">
                <label class="form-label ms-1 custom-label">Пароль</label>
                <input v-model="password" type="password" :class="{'error-glow': isSubmitted && !password}" class="form-control pretty-input" placeholder="••••••••">
              </div>

              <div style="margin-bottom: 15px;">
                <div v-if="errorMessage" class="alert alert-danger py-2 text-center m-0" style="border-radius: 12px; font-size: 14px;">
                    {{ errorMessage }}
                </div>
              </div>
                
              <button type="submit" class="btn w-100 brown-btn mb-4" :disabled="isLoading">
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                Увійти
              </button>
              
              <div class="divider mb-4">
                <span>або</span>
              </div>

              <div class="position-relative overflow-hidden mb-4 mx-auto" style="height: 48px; max-width: 320px; border-radius: 12px;">

                <button type="button" class="btn w-100 google-btn d-flex align-items-center justify-content-center h-100 position-absolute top-0 start-0">
                  <span v-if="googleLoading" class="spinner-border spinner-border-sm me-2" style="color: #625050;"></span>
                  <svg v-if="!googleLoading" class="google-icon me-2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                  </svg>
                  Увійти через Google
                </button>

                <div id="google-button-container" class="position-absolute top-0 start-0 w-100 h-100" style="opacity: 0.01; z-index: 10;"></div>

              </div>
            </form>

            <p class="bottom-text mb-0 text-center">
              Немає акаунту?
              <router-link to="/register" class="register-link">Зареєструватись</router-link>
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

.register-link {
   color: var(--color-primary); 
   text-decoration: none; 
   font-weight: 600; 
}

.register-link:hover {
  color: #240783; 
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
  padding: 40px 25px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
  transition: transform 0.3s ease;
}

.logo-image {
  height: 90px; 
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
  font-weight: 500; color: #625050; 
}

.pretty-input {
  background-color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(98, 80, 80, 0.3);
  border-radius: 12px;
  height: 48px;
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
  height: 48px;
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
  height: 48px;
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

.register-link {
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
    background-position: top center;
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