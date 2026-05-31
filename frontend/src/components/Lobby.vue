<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { roomsApi } from '../api/rooms';

const router = useRouter();
const authStore = useAuthStore();

const userName = computed(() => authStore.user?.name || authStore.user?.email?.split('@')[0] || 'Друже');

const inviteCode = ref('');
const joinError = ref('');
const joinLoading = ref(false);

const myRooms = ref([]);
const roomsLoading = ref(false);

const activeRoom = computed(() =>
  myRooms.value.find((r) => r.status === 'active') || null
);

const finishedRooms = computed(() =>
  myRooms.value.filter((r) => r.status === 'finished')
);

onMounted(async () => {
  await loadMyRooms();
});

async function loadMyRooms() {
  roomsLoading.value = true;
  try {
    const { data } = await roomsApi.getMyRooms();
    myRooms.value = data;

    if (activeRoom.value) {
      localStorage.setItem('active_room_id', activeRoom.value.id);
    } else {
      localStorage.removeItem('active_room_id');
    }
  } catch {
  } finally {
    roomsLoading.value = false;
  }
}

async function joinRoom() {
  if (!inviteCode.value.trim()) return;
  joinLoading.value = true;
  joinError.value = '';
  try {
    const { data } = await roomsApi.joinRoom(inviteCode.value.trim().toUpperCase());
    localStorage.setItem('active_room_id', data.room_id);
    router.push(`/room/${data.room_id}`);
  } catch (err) {
    joinError.value = err.response?.data?.detail || 'Помилка при приєднанні';
  } finally {
    joinLoading.value = false;
  }
}

function goToProfile() {
  router.push('/profile');
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('uk-UA', { day: 'numeric', month: 'short' });
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
                <div class="avatar-circle" @click="goToProfile" title="Профіль">
                    <i class="fa-solid fa-user text-white"></i>
                </div>
            </div>
        </header>

        <div class="flex-grow-1 d-flex align-items-center justify-content-center p-4 position-relative z-2">
            <div class="lobby-content w-100">
                
                <section class="welcome-section text-center mb-4">
                    <h1 class="fw-bold greeting-text mb-2">Привіт, {{ userName }}!</h1>
                </section>

                <div class="glass-card mb-4 text-start mx-auto">
                    <div class="form-wrapper mx-auto">
                        <h3 class="glass-card-title text-center mb-4">Куди вирушаємо сьогодні?</h3>
                        <div class="mb-3">
                            <input
                                v-model="inviteCode"
                                type="text"
                                class="form-control pretty-input text-center"
                                :class="{ 'error-glow': joinError }"
                                placeholder="Введіть код кімнати"
                                @keyup.enter="joinRoom"
                            >
                        </div>
                        
                        <div v-if="joinError" class="mb-3">
                            <div class="alert alert-danger py-2 text-center m-0" style="border-radius: 12px; font-size: 14px;">
                                {{ joinError }}
                            </div>
                        </div>

                        <button
                            @click="joinRoom"
                            class="btn brown-btn w-100"
                            :disabled="joinLoading || !inviteCode.trim()"
                        >
                            <span v-if="joinLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                            Приєднатися
                        </button>                    
                    </div>
                </div>

                <div class="divider mb-4 mx-auto">
                    <span>або</span>
                </div>

                <button @click="router.push('/create-room')" class="btn w-100 create-btn mx-auto d-block mb-5">
                    <i class="fa-solid fa-plus me-2"></i> Створити кімнату
                </button>

                <div v-if="roomsLoading" class="text-center py-3">
                    <div class="spinner-border spinner-border-sm" style="color: #292CA8;"></div>
                </div>

                <div v-else-if="myRooms.length > 0" class="my-rooms-section">
                    <p class="section-label mb-3">Мої прогулянки</p>

                    <div
                        v-for="room in myRooms"
                        :key="room.id"
                        class="glass-box room-card d-flex align-items-center px-3 py-3 mb-3"
                        @click="router.push(`/room/${room.id}`)"
                    >
                        <div class="room-icon me-3" :class="room.status === 'active' ? 'icon-active' : 'icon-finished'">
                            <i class="fa-solid" :class="room.status === 'active' ? 'fa-location-dot' : 'fa-flag-checkered'"></i>
                        </div>
                        <div class="flex-grow-1 min-w-0">
                            <div class="room-name fw-bold text-truncate">{{ room.name }}</div>
                            <div class="room-meta">{{ formatDate(room.created_at) }}</div>
                        </div>
                        <span class="room-badge ms-2" :class="room.status === 'active' ? 'badge-active' : 'badge-finished'">
                            {{ room.status === 'active' ? 'Активна' : 'Завершена' }}
                        </span>
                    </div>
                </div>
                
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
    top: 0;
    bottom: 0;
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

.mini-title { font-size: 20px; color: #ffffff; }

.avatar-circle {
    width: 40px;
    height: 40px;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.2s;
}
.avatar-circle:hover { background-color: rgba(255, 255, 255, 0.35); }

.lobby-content {
    width: 100%;
    max-width: 400px;
}

.greeting-text { font-size: 30px; color: #292CA8; }

.glass-card {
    width: 100%;
    max-width: 400px; 
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 24px;
    padding: 40px 25px; 
    margin-top: 35px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
}

.form-wrapper { max-width: 320px; }

.glass-card-title {
    font-weight: 700; 
    color: #292CA8; 
    font-size: 20px; 
    letter-spacing: -0.5px;
}

.pretty-input {
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(98, 80, 80, 0.3);
    border-radius: 12px;
    height: 48px;
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
    max-width: 400px;
}
.create-btn:hover { background-color: rgba(255, 255, 255, 0.8); }

.divider {
    display: flex;
    align-items: center;
    color: #625050; 
    opacity: 0.6; 
    max-width: 400px;
}

.divider::before, .divider::after {
    content: "";
    flex: 1;
    border-bottom: 1px solid #625050; 
}

.divider span { padding: 0 15px; font-size: 14px; }

.text-dark-brown { color: #3b1c1c; }

.glass-box {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 20px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
}

.active-trip-banner { border-left: 5px solid #292CA8; width: 100%; }

.banner-icon {
    width: 40px;
    height: 40px;
    background-color: #292CA8;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(41, 44, 165, 0.2);
}

.section-label {
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #625050;
    opacity: 0.7;
}

.room-card {
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.room-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(31, 38, 135, 0.1) !important;
}

.room-icon {
    width: 42px;
    height: 42px;
    border-radius: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}
.icon-active  { background-color: rgba(41, 44, 165, 0.12); color: #292CA8; }
.icon-finished { background-color: rgba(98, 80, 80, 0.1); color: #625050; }

.room-name  { font-size: 15px; color: #3b1c1c; }
.room-meta  { font-size: 12px; color: #625050; opacity: 0.7; margin-top: 1px; }

.room-badge {
    font-size: 11px;
    font-weight: 700;
    border-radius: 20px;
    padding: 3px 10px;
    white-space: nowrap;
    flex-shrink: 0;
}
.badge-active   { background: rgba(41, 44, 165, 0.1);  color: #292CA8; }
.badge-finished { background: rgba(98, 80, 80, 0.1);   color: #625050; }
</style>