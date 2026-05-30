<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { roomsApi } from '../api/rooms';

const router = useRouter();

const roomName = ref('');
const isSubmitted = ref(false);
const errorMessage = ref('');
const isLoading = ref(false);

async function handleCreate() {
  isSubmitted.value = true;
  errorMessage.value = '';

  if (!roomName.value.trim()) return;

  isLoading.value = true;
  try {
    const { data } = await roomsApi.createRoom(roomName.value.trim());
    localStorage.setItem('active_room_id', data.id);
    router.push(`/room/${data.id}`);
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Помилка при створенні кімнати';
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="lobby-page d-flex flex-column min-vh-100 position-relative">

    <div class="map-pillar pillar-left d-none d-lg-block"></div>
    <div class="map-pillar pillar-right d-none d-lg-block"></div>

    <header class="lobby-header d-flex justify-content-between align-items-center px-4 py-3 position-relative z-3">
      <div class="d-flex align-items-center">
        <img src="../assets/logo.svg" alt="Logo" class="mini-logo me-2">
        <h2 class="fw-bold mb-0 mini-title">RouteSplitter</h2>
      </div>
      <div class="d-flex align-items-center gap-3">
        <button @click="logout" class="btn btn-sm logout-btn">Вийти</button>
          <div class="avatar-circle">
            <i class="fa-solid fa-user text-white"></i>
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
                class="alert alert-warning py-2 text-center m-0"
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
              <i v-else class="fa-solid fa-plus me-2"></i>
              Створити кімнату
            </button>

            <button @click="router.push('/lobby')" class="btn create-btn w-100">
              Скасувати
            </button>

          </div>
        </div>

        <p class="hint-text text-center mt-4 mx-auto">
          <i class="fa-solid fa-circle-info me-1"></i>
          Після створення ти отримаєш код запрошення,<br>
          яким зможеш поділитися з друзями
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

.mini-logo { height: 35px; }

.mini-title {
  font-size: 20px;
  color: #ffffff;
}

.logout-btn {
    color: rgba(255,255,255,0.8);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 10px;
    font-size: 13px;
}
.logout-btn:hover { color: #fff; border-color: #fff; }

.avatar-circle {
    width: 40px;
    height: 40px;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

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
  background-color: rgba(255, 255, 255, 0.8); 
}

.hint-text {
  font-size: 13px;
  color: #625050;
  opacity: 0.65;
  max-width: 340px;
  line-height: 1.5;
}
</style>