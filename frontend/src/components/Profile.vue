<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { roomsApi } from '../api/rooms';

const router = useRouter();
const authStore = useAuthStore();

const user = computed(() => authStore.user);
const userName = computed(() => user.value?.name || user.value?.email?.split('@')[0] || 'Мандрівник');
const userEmail = computed(() => user.value?.email || '—');

const initials = computed(() => {
  const name = user.value?.name || '';
  if (!name) return '?';
  return name.split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase();
});

const myRooms = ref([]);
const statsLoading = ref(true);

const totalRooms = computed(() => myRooms.value.length);
const activeRooms = computed(() => myRooms.value.filter((r) => r.status === 'active').length);
const finishedRooms = computed(() => myRooms.value.filter((r) => r.status === 'finished').length);

const recentRooms = computed(() => myRooms.value.slice(0, 5));

onMounted(async () => {
  try {
    const { data } = await roomsApi.getMyRooms();
    myRooms.value = data;
  } catch {
    // мовчки
  } finally {
    statsLoading.value = false;
  }
});

function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('uk-UA', {
    day: 'numeric', month: 'long', year: 'numeric',
  });
}

function formatDateShort(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('uk-UA', { day: 'numeric', month: 'short' });
}

function logout() {
  authStore.logout();
  localStorage.removeItem('active_room_id');
  router.push('/');
}

</script>

<template>
  <div class="lobby-page d-flex flex-column min-vh-100 position-relative">

    <div class="map-pillar pillar-left d-none d-lg-block"></div>
    <div class="map-pillar pillar-right d-none d-lg-block"></div>

    <header class="profile-header d-flex justify-content-between align-items-center px-4 py-3 position-relative z-3">
      <div class="d-flex align-items-center">
        <i class="fa-solid fa-chevron-left back-icon me-3" @click="router.push('/lobby')"></i>
        <h2 class="fw-bold mb-0 mini-title">Профіль</h2>
      </div>
    </header>

    <div class="flex-grow-1 d-flex justify-content-center p-4 position-relative z-2">
      <div class="profile-content w-100">

        <div class="text-center mb-4 mt-2">
          <div class="big-avatar mx-auto mb-3">
            <span class="initials-text">{{ initials }}</span>
          </div>
          <h2 class="fw-bold profile-name mb-1">{{ userName }}</h2>
          <p class="profile-email mb-0">{{ userEmail }}</p>
        </div>

        <div class="stats-row d-flex gap-3 mb-4">
          <div class="glass-box stat-card flex-1 text-center py-3 px-2">
            <div v-if="statsLoading" class="spinner-border spinner-border-sm" style="color:#292CA8;"></div>
            <template v-else>
              <div class="stat-number">{{ totalRooms }}</div>
              <div class="stat-label">Прогулянок</div>
            </template>
          </div>
          <div class="glass-box stat-card flex-1 text-center py-3 px-2">
            <div v-if="statsLoading" class="spinner-border spinner-border-sm" style="color:#292CA8;"></div>
            <template v-else>
              <div class="stat-number text-active">{{ activeRooms }}</div>
              <div class="stat-label">Активних</div>
            </template>
          </div>
          <div class="glass-box stat-card flex-1 text-center py-3 px-2">
            <div v-if="statsLoading" class="spinner-border spinner-border-sm" style="color:#292CA8;"></div>
            <template v-else>
              <div class="stat-number text-finished">{{ finishedRooms }}</div>
              <div class="stat-label">Завершених</div>
            </template>
          </div>
        </div>

        <div class="glass-box p-4 mb-4">
          <p class="section-label mb-3">Інформація</p>

          <div class="info-row d-flex align-items-center py-2">
            <div class="info-icon me-3"><i class="fa-solid fa-user"></i></div>
            <div>
              <div class="info-label">Ім'я</div>
              <div class="info-value">{{ userName }}</div>
            </div>
          </div>

          <div class="info-divider"></div>

          <div class="info-row d-flex align-items-center py-2">
            <div class="info-icon me-3"><i class="fa-solid fa-envelope"></i></div>
            <div>
              <div class="info-label">Email</div>
              <div class="info-value">{{ userEmail }}</div>
            </div>
          </div>

        </div>

        <div v-if="!statsLoading && recentRooms.length > 0" class="mb-4">
          <p class="section-label mb-3">Останні прогулянки</p>

          <div
            v-for="room in recentRooms"
            :key="room.id"
            class="glass-box room-card d-flex align-items-center px-3 py-3 mb-3"
            @click="router.push(`/room/${room.id}`)"
          >
            <div class="room-icon me-3" :class="room.status === 'active' ? 'icon-active' : 'icon-finished'">
              <i class="fa-solid" :class="room.status === 'active' ? 'fa-location-dot' : 'fa-flag-checkered'"></i>
            </div>
            <div class="flex-grow-1 min-w-0">
              <div class="room-name fw-bold text-truncate">{{ room.name }}</div>
              <div class="room-meta">{{ formatDateShort(room.created_at) }}</div>
            </div>
            <span class="room-badge ms-2" :class="room.status === 'active' ? 'badge-active' : 'badge-finished'">
              {{ room.status === 'active' ? 'Активна' : 'Завершена' }}
            </span>
          </div>
        </div>

        <button @click="logout" class="btn w-100 logout-bottom-btn mb-4">
          <i class="fa-solid fa-right-from-bracket me-2"></i>
          Вийти з акаунту
        </button>

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
  min-height: 100vh;
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

.profile-header {
  background-color: #625050;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.mini-title { font-size: 20px; color: #ffffff; }

.back-icon {
  font-size: 18px;
  color: rgba(255,255,255,0.85);
  cursor: pointer;
  transition: color 0.2s;
}
.back-icon:hover { color: #fff; }

.profile-content {
  max-width: 400px;
}

.big-avatar {
  width: 88px;
  height: 88px;
  background: linear-gradient(135deg, #292CA8 0%, #625050 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(41, 44, 165, 0.25);
}

.initials-text {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 1px;
}

.profile-name { font-size: 24px; color: #292CA8; }
.profile-email { font-size: 14px; color: #625050; opacity: 0.8; }

.stats-row { align-items: stretch; }

.stat-card {
  flex: 1;
  border-radius: 18px !important;
}

.stat-number {
  font-size: 26px;
  font-weight: 700;
  color: #292CA8;
  line-height: 1;
}
.text-active   { color: #2e7d32; }
.text-finished { color: #625050; }

.stat-label {
  font-size: 11px;
  font-weight: 600;
  color: #625050;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 4px;
}

.glass-box {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);
}

.section-label {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #625050;
  opacity: 0.7;
  margin-bottom: 0;
}

.info-divider {
  border-bottom: 1px solid rgba(98, 80, 80, 0.12);
}

.info-icon {
  width: 42px;
  height: 42px;
  background: rgba(41, 44, 165, 0.08);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #292CA8;
  font-size: 15px;
  flex-shrink: 0;
}

.info-label { font-size: 11px; color: #625050; opacity: 0.65; font-weight: 500; }
.info-value  { font-size: 15px; color: #3b1c1c; font-weight: 600; }

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
.icon-active   { background-color: rgba(41, 44, 165, 0.12); color: #292CA8; }
.icon-finished { background-color: rgba(98, 80, 80, 0.1); color: #625050; }

.room-name { font-size: 15px; color: #3b1c1c; }
.room-meta { font-size: 12px; color: #625050; opacity: 0.7; margin-top: 1px; }

.room-badge {
  font-size: 11px;
  font-weight: 700;
  border-radius: 20px;
  padding: 3px 10px;
  white-space: nowrap;
  flex-shrink: 0;
}
.badge-active   { background: rgba(41, 44, 165, 0.1); color: #292CA8; }
.badge-finished { background: rgba(98, 80, 80, 0.1); color: #625050; }

.logout-bottom-btn {
  background: rgba(255, 255, 255, 0.6);
  color: #c0392b;
  border: 1px solid rgba(192, 57, 43, 0.3);
  height: 48px;
  border-radius: 14px;
  font-weight: 600;
  font-size: 15px;
  backdrop-filter: blur(8px);
  transition: all 0.2s;
}
.logout-bottom-btn:hover {
  background: rgba(192, 57, 43, 0.08);
  border-color: rgba(192, 57, 43, 0.5);
}
</style>