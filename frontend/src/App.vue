<script setup>

/**
 * @file Root component of the application (App.vue).
 * Responsible for rendering matching views via the router-view and 
 * displaying a global full-screen overlay loader if the backend server is sleeping.
 */

import { isServerWakingUp } from './api/client';

/**
 * @description Reactive state imported from the API client indicating 
 * whether the backend server is undergoing a "cold start" (waking up).
 * @type {import('vue').Ref<boolean>}
 */
</script>

<template>
  <router-view></router-view>

  <div v-if="isServerWakingUp" class="global-loader-overlay d-flex align-items-center justify-content-center">
    <div class="glass-loader-card p-5 text-center fade-in mx-3">
      <div class="icon-wrapper mx-auto mb-4">
        <i class="fa-solid fa-server fa-bounce fs-1" style="color: #292CA8;"></i>
      </div>
      <h3 class="fw-bold mb-3" style="color: #3b1c1c;">Прокидаємо сервер...</h3>
      <p class="text-muted small mb-4">
        Це перший запит після довгої паузи.<br>
        Серверу може знадобитися близько 30-50 секунд, щоб запуститися. <br>
        Будь ласка, трохи зачекайте
      </p>
      <div class="spinner-border" style="color: #292CA8;" role="status"></div>
    </div>
  </div>
</template>

<style scoped>
/* Scoped CSS styling for background blur, glassmorphism modal card, and entry animations */
.global-loader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(98, 80, 80, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 9999;
}

.glass-loader-card {
  max-width: 450px;
  width: 100%;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.15);
}

.icon-wrapper {
  width: 80px;
  height: 80px;
  background-color: rgba(41, 44, 165, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fade-in {
  animation: fadeInModal 0.4s ease-out forwards;
}

@keyframes fadeInModal {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>