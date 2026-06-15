<script setup>
/**
 * @file CreatingRoom.vue
 * @description Frontend Single File Component providing an interface to initialize and spawn 
 * a new walk session workspace (room). Handles layout styling overlays, character metrics, 
 * input validations, and error parsing states.
 */

import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { roomsApi } from '../api/rooms';
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
 * Bound reactive textual field representing the user's customized title name string for the session.
 * @type {import('vue').Ref<string>}
 */
const roomName = ref('');

/**
 * Validation tracking state indicating whether the creation submission form has been triggered.
 * @type {import('vue').Ref<boolean>}
 */
const isSubmitted = ref(false);

/**
 * Text contextual message body holding operational error details caught during backend queries.
 * @type {import('vue').Ref<string>}
 */
const errorMessage = ref('');

/**
 * Network state loading indicator displaying template spinner wheels and locking down input interfaces.
 * @type {import('vue').Ref<boolean>}
 */
const isLoading = ref(false);

/**
 * Evaluates the authenticated profile instance context to derive active avatar media elements.
 * @type {import('vue').ComputedRef<string|null>}
 */
const currentUserAvatar = computed(() => authStore.user?.avatar);

/**
 * Validates form parameters and fires an administrative API request to spawn a workspace room instance.
 * Updates local cache parameters and moves focus routes onto the newly constructed dashboard view.
 * * @async
 * @function handleCreate
 * @returns {Promise<void>} Resolves once navigation routes change or backend exceptions handle.
 */
async function handleCreate() {
  isSubmitted.value = true;
  errorMessage.value = '';

  if (!roomName.value.trim()) return;

  isLoading.value = true;
  try {
    /** @constant {Object} response - API creation response structure containing room descriptors. */
    const { data } = await roomsApi.createRoom(roomName.value.trim());
    localStorage.setItem('active_room_id', data.id);
    router.push(`/room/${data.id}`);
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Помилка при створенні кімнати';
  } finally {
    isLoading.value = false;
  }
}

/**
 * Dispatches navigation requests redirecting operational interface windows to the personal User Profile page.
 * @function goToProfile
 */
function goToProfile() {
  router.push('/profile');
}

/**
 * Triggers structural layout routing shifts returning active windows back to the primary Main Lobby page.
 * @function leaveRoom
 */
const leaveRoom = () => {
  router.push('/lobby');
}

</script>

<template>
  <div class="lobby-page d-flex flex-column min-vh-100 position-relative">

    <div class="map-pillar pillar-left d-none d-lg-block"></div>
    <div class="map-pillar pillar-right d-none d-lg-block"></div>

    <header class="lobby-header d-flex justify-content-between align-items-center px-4 py-3 position-relative z-3">
      <div class="d-flex align-items-center">
        <i class="fa-solid fa-chevron-left back-icon me-3" @click="leaveRoom"></i>
      </div>
      <div class="d-flex align-items-center gap-3">
          <div class="avatar-circle overflow-hidden" @click="goToProfile" title="Профіль">
            <img v-if="currentUserAvatar" :src="currentUserAvatar" alt="Профіль" class="w-100 h-100" style="object-fit: cover;" />
            <i v-else class="fa-solid fa-user text-white"></i>
          </div>
      </div>
    </header>

    <div class="flex-grow-1 d-flex align-items-center justify-content-center p-4 position-relative z-2">
      <div class="lobby-content w-100">

        <section class="welcome-section text-center mb-2">
          <h1 class="fw-bold greeting-text mb-1">Нова прогулянка</h1>
          <p class="subtitle-text">Створіть власну пригоду!</p>
        </section>

        <div class="glass-card text-start mx-auto">
          <div class="form-wrapper mx-auto">

            <div class="mb-4 text-start">
              <div class="d-flex justify-content-between align-items-center mb-1 px-1">
                <label class="form-label ms-1 custom-label">Назва прогулянки</label>
                <span class="char-counter">{{ roomName.length }}/60</span>
              </div>
              <input
                v-model="roomName"
                type="text"
                class="form-control pretty-input"
                :class="{ 'error-glow': isSubmitted && !roomName.trim() }"
                placeholder="Введіть назву прогулянки"
                maxlength="60"
                @keyup.enter="handleCreate"
                autofocus
              >
            </div>

            <div v-if="errorMessage || (isSubmitted && !roomName.trim())" class="mb-4">
              <div
                v-if="errorMessage"
                class="alert alert-danger py-2 text-center m-0"
                style="border-radius: 12px; font-size: 14px;"
              >
                {{ errorMessage }}
              </div>
              <div
                v-else-if="isSubmitted && !roomName.trim()"
                class="alert alert-danger py-2 text-center m-0"
                style="border-radius: 12px; font-size: 14px;"
              >
                Введіть назву прогулянки
              </div>
            </div>

            <button
              @click="handleCreate"
              class="btn brown-btn w-100 mb-3"
              :disabled="isLoading"
            >
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <i v-else class="fa-solid me-2"></i>
              Створити кімнату
            </button>

            <button @click="router.push('/lobby')" class="btn create-btn w-100">
              Скасувати
            </button>

          </div>
        </div>

        <p class="hint-text text-center mt-4 mx-auto">
          <i class="fa-solid fa-circle-info me-1"></i>
          Після створення кімнати буде згенеровано код запрошення, який можна надіслати друзям для приєднання.
        </p>

      </div>
    </div>
  </div>
</template>

<style scoped>
.lobby-page {
  background-color: var(--bg-main);
  background-image: 
    radial-gradient(circle at 80% 20%, rgba(100, 109, 210, 0.3) 0%, rgba(98, 80, 80, 0) 40%),
    radial-gradient(circle at 20% 80%, rgba(100, 109, 210, 0.3) 0%, rgba(100, 109, 210, 0) 45%);
  width: 100%;
  overflow: hidden;
}

.map-pillar {
  position: fixed;
  top: 0; bottom: 0;
  width: 35vw;
  z-index: 1;
}

.pillar-left {
  left: 0;
  background: linear-gradient(135deg, rgba(41, 44, 165, 0.7) 0%, rgba(26, 28, 106, 0.8) 100%), url('../assets/map.jpg');
  background-size: cover;
  background-position: left center;
  -webkit-mask-image: linear-gradient(to right, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%);
  mask-image: linear-gradient(to right, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%);
}

.pillar-right {
  right: 0;
  background: linear-gradient(135deg, rgba(41, 44, 165, 0.7) 0%, rgba(26, 28, 106, 0.8) 100%), url('../assets/map.jpg');
  background-size: cover;
  background-position: right center;
  -webkit-mask-image: linear-gradient(to left, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%);
  mask-image: linear-gradient(to left, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%);
}

.lobby-header {
  background-color: #625050;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.back-icon {
    font-size: 20px;
    color: #ffffff;
    cursor: pointer;
    transition: transform 0.2s;
}

.back-icon:active {
    transform: scale(0.9);
}

.avatar-circle {
    width: 40px;
    height: 40px;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.avatar-circle:hover { background-color: rgba(255, 255, 255, 0.35); }

.lobby-content {
  width: 100%;
  max-width: 400px;
}

.greeting-text {
  font-size: 30px;
  color: #292CA8;
}

.subtitle-text {
  font-size: 15px;
  color: #625050;
  opacity: 0.8;
}

.glass-card {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 24px;
  padding: 40px 25px;
  margin-top: 28px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
}

.form-wrapper { max-width: 320px; }

.glass-card-title {
  font-weight: 700;
  color: #292CA8;
  font-size: 20px;
  letter-spacing: -0.5px;
}

.custom-label { 
  font-weight: 500; 
  color: #625050; 
  font-size: 14px;
}

.pretty-input {
  background-color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(98, 80, 80, 0.3);
  border-radius: 12px;
  height: 48px;
  font-size: 15px;
}

.pretty-input:focus {
  background-color: #ffffff;
  border-color: #292CA8;
  box-shadow: 0 0 0 2px rgba(41, 44, 165, 0.2);
}

.error-glow {
  border-color: #e05858 !important;
  box-shadow: 0 0 0 2px rgba(224, 88, 88, 0.2) !important;
}

.char-counter {
  font-size: 12px;
  color: #625050;
  opacity: 0.6;
  font-weight: 500;
}

.examples-row { 
  gap: 8px; 
}

.example-chip {
  background: rgba(41, 44, 165, 0.08);
  color: #292CA8;
  border: 1px solid rgba(41, 44, 165, 0.2);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  white-space: nowrap;
}

.example-chip:hover {
  background: rgba(41, 44, 165, 0.15);
  border-color: rgba(41, 44, 165, 0.4);
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
.brown-btn:hover:not(:disabled) { background-color: #4a3c3c; }
.brown-btn:disabled { opacity: 0.65; cursor: not-allowed; }

.create-btn {
  background-color: #ffffff;
  color: #625050;
  border: 1px solid rgba(98, 80, 80, 0.4);
  height: 48px;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
}
.create-btn:hover { 
  background-color: #f9ecec8a; 
}

.hint-text {
  font-size: 13px;
  color: #625050;
  opacity: 0.65;
  max-width: 340px;
  line-height: 1.5;
}
</style>