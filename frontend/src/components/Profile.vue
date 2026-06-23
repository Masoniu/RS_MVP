<script setup>
/**
 * @file Profile.vue
 * @description User Profile component. Manages personal identification information modifications,
 * security credential updates, session metrics aggregation, archive history tracking, 
 * and external Google OAuth identity linking handshakes.
 */

import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { roomsApi } from '../api/rooms';

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
 * The unique Google API Credentials Client ID fetched from environment variables.
 * @constant {string|undefined} GOOGLE_CLIENT_ID
 */
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

/**
 * Reactive mirror pulling the active user record model straight from the core Pinia store.
 * @type {import('vue').ComputedRef<Object|null>}
 */
const user = computed(() => authStore.user);

/**
 * Extractable textual user descriptor string. 
 * Falls back to name, email prefix, or a localized Ukrainian fallback phrase ("Мандрівник").
 * @type {import('vue').ComputedRef<string>}
 */
const userName = computed(() => user.value?.name || user.value?.email?.split('@')[0] || 'Мандрівник');

/**
 * User email address string proxy, defaulting to an empty spacer if unassigned.
 * @type {import('vue').ComputedRef<string>}
 */
const userEmail = computed(() => user.value?.email || '—');

/**
 * Generates up to a two-letter textual placeholder initials badge from the user's name fields.
 * Returns a "?" fallback string if the name data is completely empty.
 * @type {import('vue').ComputedRef<string>}
 */
const initials = computed(() => {
  const name = user.value?.name || '';
  if (!name) return '?';
  return name.split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase();
});

/**
 * Collection index capturing all operational room entities linked to the active profile account.
 * @type {import('vue').Ref<Array<Object>>}
 */
const myRooms = ref([]);

/**
 * Structural loading tracker displaying shell skeletons while statistics load asynchronously.
 * @type {import('vue').Ref<boolean>}
 */
const statsLoading = ref(true);

/**
 * Total combined historical rooms assigned to the current active user record.
 * @type {import('vue').ComputedRef<number>}
 */
const totalRooms = computed(() => myRooms.value.length);

/**
 * Total count of rooms currently in an active operational state status.
 * @type {import('vue').ComputedRef<number>}
 */
const activeRooms = computed(() => myRooms.value.filter((r) => r.status === 'active').length);

/**
 * Total count of rooms that have been finalized and marked with a finished status flag.
 * @type {import('vue').ComputedRef<number>}
 */
const finishedRooms = computed(() => myRooms.value.filter((r) => r.status === 'finished').length);

/**
 * Computes a filtered subset containing exclusively historical room records with a finished status.
 * @type {import('vue').ComputedRef<Array<Object>>}
 */
const finishedRoomList = computed(() => myRooms.value.filter((r) => r.status === 'finished'));

/**
 * UI visual toggle flag managing the visibility of the past finished rooms list panel.
 * @type {import('vue').Ref<boolean>}
 */
const showHistory = ref(false);

/**
 * UI toggle flag rendering the layout confirmation modal overlay when triggering standard account logout.
 * @type {import('vue').Ref<boolean>}
 */
const showLogoutModal = ref(false);

/**
 * UI toggle flag displaying or hiding the profile editor dialog modal window wrapper.
 * @type {import('vue').Ref<boolean>}
 */
const showEditModal = ref(false);

/**
 * Tracks the current sub-panel tab selected within the edit modal overlay ('info' or 'password').
 * @type {import('vue').Ref<string>}
 */
const editTab = ref('info');

/**
 * Temporary form text string tracking changes to the user's full name inside the info editor panel.
 * @type {import('vue').Ref<string>}
 */
const editName = ref('');

/**
 * Temporary form text string tracking changes to the user's email address inside the info editor panel.
 * @type {import('vue').Ref<string>}
 */
const editEmail = ref('');

/**
 * General info form submission loader locking interactive inputs during update queries.
 * @type {import('vue').Ref<boolean>}
 */
const editLoading = ref(false);

/**
 * Container holding validation error description texts caught during profile detail mutations.
 * @type {import('vue').Ref<string>}
 */
const editError = ref('');

/**
 * Container holding flash confirmation success messages post successful information payload synchronization.
 * @type {import('vue').Ref<string>}
 */
const editSuccess = ref('');

/**
 * Form field mapping verification variable checking the user's current security password.
 * @type {import('vue').Ref<string>}
 */
const currentPassword = ref('');

/**
 * Form field mapping placeholder holding the new replacement password string.
 * @type {import('vue').Ref<string>}
 */
const newPassword = ref('');

/**
 * Form field mapping checking matching characters to confirm the newly specified password parameter.
 * @type {import('vue').Ref<string>}
 */
const confirmPassword = ref('');

/**
 * Password form submission loader displaying text spinner wheels during mutation requests.
 * @type {import('vue').Ref<boolean>}
 */
const pwdLoading = ref(false);

/**
 * Feedback string mapping system security processing errors thrown by change password routines.
 * @type {import('vue').Ref<string>}
 */
const pwdError = ref('');

/**
 * Feedback confirmation string flashing notices showing a successful password transition update.
 * @type {import('vue').Ref<string>}
 */
const pwdSuccess = ref('');

/**
 * Pre-populates the input text fields with active user parameters and opens up the profile edit modal overlay.
 * @function openEditModal
 * @returns {void}
 */
function openEditModal() {
  editName.value = user.value?.name || '';
  editEmail.value = user.value?.email || '';
  editError.value = '';
  editSuccess.value = '';
  pwdError.value = '';
  pwdSuccess.value = '';
  currentPassword.value = '';
  newPassword.value = '';
  confirmPassword.value = '';
  editTab.value = 'info';
  showEditModal.value = true;
}

/**
 * Closes out active visibility flags shutting down the profile modal editor box component.
 * @function closeEditModal
 * @returns {void}
 */
function closeEditModal() {
  showEditModal.value = false;
}

/**
 * Compares form field adjustments and sends profile mutation update payloads to the core API store.
 * * @async
 * @function saveProfile
 * @returns {Promise<void>} Resolves when the profile parameters synchronize or exceptions process.
 */
async function saveProfile() {
  editError.value = '';
  editSuccess.value = '';
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (editEmail.value.trim() && !emailRegex.test(editEmail.value.trim())) {
    editError.value = 'Будь ласка, введіть коректний email (наприклад, user@mail.com)';
    return;
  }

  /** @type {Object} payload - Dynamically calculated map filtering only changed properties. */
  const payload = {};
  if (editName.value.trim() && editName.value.trim() !== user.value?.name) {
    payload.name = editName.value.trim();
  }
  if (editEmail.value.trim() && editEmail.value.trim() !== user.value?.email) {
    payload.email = editEmail.value.trim();
  }

  // Exit early if the form fields match the existing user details perfectly
  if (!Object.keys(payload).length) {
    editSuccess.value = 'Змін немає';
    return;
  }

  editLoading.value = true;
  try {
    await authStore.updateProfile(payload);
    editSuccess.value = 'Збережено!';
    setTimeout(() => { editSuccess.value = ''; }, 2000);
  } catch (e) {
    if (e.response?.status === 422) {
        editError.value = 'Введено некоректні дані формату';
    } else {
        editError.value = e.response?.data?.detail || 'Помилка збереження';
    }
  } finally {
    editLoading.value = false;
  }
}

/**
 * Performs validation parsing rules and coordinates password update actions against core secure APIs.
 * * @async
 * @function savePassword
 * @returns {Promise<void>} Resolves when the security database entry transforms.
 */
async function savePassword() {
  pwdError.value = '';
  pwdSuccess.value = '';
  
  if (!currentPassword.value) {
    pwdError.value = 'Введіть поточний пароль';
    return;
  }
  if (newPassword.value !== confirmPassword.value) {
    pwdError.value = 'Паролі не співпадають';
    return;
  }
  
  pwdLoading.value = true;
  try {
    await authStore.changePassword(currentPassword.value, newPassword.value);
    pwdSuccess.value = 'Пароль змінено!';
    currentPassword.value = '';
    newPassword.value = '';
    confirmPassword.value = '';
    setTimeout(() => { pwdSuccess.value = ''; }, 2500);
  } catch (e) {
    pwdError.value = e.response?.data?.detail || 'Помилка зміни паролю';
  } finally {
    pwdLoading.value = false;
  }
}

/**
 * Check verifying if the active user profile profile has been linked to a federated Google credential layers.
 * @type {import('vue').ComputedRef<boolean>}
 */
const isGoogleLinked = computed(() => user.value?.googleLinked);

/**
 * Social account handshake loading indicator toggled while binding tokens.
 * @type {import('vue').Ref<boolean>}
 */
const linkLoading = ref(false);

/**
 * Intercepts authorization signatures emitted by Google popup widgets and appends them onto standard account profiles.
 * * @async
 * @function handleLinkGoogle
 * @param {Object} response - Credential payload dictionary emitted via native web elements.
 * @param {string} response.credential - Raw authorization string token verification format signature.
 * @returns {Promise<void>} Resolves once social accounts mesh.
 */
const handleLinkGoogle = async (response) => {
  linkLoading.value = true;
  try {
    await authStore.linkGoogleAccount(response.credential);
  } catch (error) {
    alert(error.response?.data?.detail || 'Не вдалося прив\'язати акаунт');
  } finally {
    linkLoading.value = false;
  }
};

/**
 * Core initialization mounting hook. Queries the application backend database to retrieve user history metrics
 * and configures the identity rendering framework needed to construct Google interaction buttons.
 */
onMounted(async () => {
  try {
    const { data } = await roomsApi.getMyRooms();
    myRooms.value = data;
  } catch {
    // Graceful recovery placeholder block protecting initial dashboard load workflows
  } finally {
    statsLoading.value = false;
  }

  // Configure and display standard Google connection options if the profile is unlinked
  if (window.google && GOOGLE_CLIENT_ID && !isGoogleLinked.value) {
    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: handleLinkGoogle,
    });

    window.google.accounts.id.renderButton(
      document.getElementById('profile-google-button'),
      { theme: 'outline', size: 'large' }
    );
  }
});

/**
 * Formats standard date-time string objects into readable calendar values matching localized standards.
 * * @style Standard structure configuration example: "15 Jun"
 * @function formatDateShort
 * @param {string} dateStr - Raw date-time serialization format returned by backend endpoints.
 * @returns {string} Formatted localized short textual calendar representation string.
 */
function formatDateShort(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('uk-UA', { day: 'numeric', month: 'short' });
}

/**
 * Invalidates system access tokens, flushes active storage caches, and redirects view scopes to root welcome panels.
 * @function confirmLogout
 * @returns {void}
 */
function confirmLogout() {
  authStore.logout();
  localStorage.removeItem('active_room_id');
  router.push('/');
}
</script>

<template>
  <div class="profile-page d-flex flex-column min-vh-100 position-relative">

    <div class="map-pillar pillar-left d-none d-lg-block"></div>
    <div class="map-pillar pillar-right d-none d-lg-block"></div>

    <header class="profile-header d-flex justify-content-between align-items-center px-4 py-3 position-fixed top-0 start-0 w-100 z-3">
      <div class="d-flex align-items-center">
        <i class="fa-solid fa-chevron-left back-icon me-3" @click="router.push('/lobby')"></i>
        <h2 class="fw-bold mb-0 mini-title">Профіль</h2>
      </div>
    </header>

    <div class="flex-grow-1 d-flex justify-content-center p-4 position-relative z-2" style="margin-top: 80px;">
      <div class="profile-content w-100 mx-auto" style="max-width: 900px;">

        <div class="text-center mb-4 mt-2">
          <div class="big-avatar mx-auto mb-3 overflow-hidden">
            <img v-if="user?.avatar" :src="user.avatar" alt="Avatar" class="w-100 h-100" style="object-fit: cover;" />
            <span v-else class="initials-text">{{ initials }}</span>
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
        
          <div class="d-flex justify-content-between align-items-center mb-3">
            <p class="section-label mb-0">Інформація та безпека</p>

            <button class="btn edit-header-btn" @click="openEditModal">
              <i class="fa-solid fa-pen me-2"></i>Редагувати
            </button>
          </div>

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

          <div class="info-divider"></div>

          <div class="info-row d-flex align-items-center justify-content-between py-3">
            <div class="d-flex align-items-center">
                <div class="info-icon me-3" style="background: rgba(234, 67, 53, 0.1); color: #EA4335;">
                    <i class="fa-brands fa-google"></i>
                </div>
                <div>
                    <div class="info-label">Google Акаунт</div>
                    <div class="info-value">
                        <span v-if="isGoogleLinked" class="text-success"><i class="fa-solid fa-check-circle me-1"></i> Прив'язано</span>
                        <span v-else class="text-muted">Не прив'язано</span>
                    </div>
                </div>
            </div>

            <div v-if="!isGoogleLinked" class="position-relative overflow-hidden" style="width: 130px; height: 40px; border-radius: 10px;">
                <button class="btn btn-sm btn-outline-primary fw-bold w-100 h-100 position-absolute top-0 start-0" :disabled="linkLoading" style="border-radius: 10px; z-index: 1;">
                    <span v-if="linkLoading" class="spinner-border spinner-border-sm"></span>
                    <span v-else>Прив'язати</span>
                </button>
                <div id="profile-google-button" class="position-absolute top-0 start-0 w-100 h-100" style="opacity: 0.01; z-index: 10;"></div>
            </div>
          </div>
        </div>

        <div v-if="!statsLoading && finishedRoomList.length > 0" class="history-section mt-2 pb-5">
          <button v-if="!showHistory" @click="showHistory = true" class="btn create-btn w-100 mx-auto d-block" style="max-width: 400px;">
            <i class="fa-solid fa-clock-rotate-left me-2"></i> Переглянути історію прогулянок
          </button>

          <div v-if="showHistory" class="history-grid-wrapper fade-in">
            <div class="d-flex justify-content-between align-items-center mb-3 mt-4">
              <p class="section-label mb-0">Завершені прогулянки</p>
              <button @click="showHistory = false" class="btn btn-sm text-muted" style="background: none; border: none;">
                <i class="fa-solid fa-chevron-up me-1"></i> Згорнути
              </button>
            </div>

            <div class="row g-3">
              <div v-for="room in finishedRoomList" :key="room.id" class="col-12 col-md-6 col-lg-4">
                <div class="glass-box room-card d-flex align-items-center px-3 py-3 h-100" @click="router.push(`/room/${room.id}`)">
                  <div class="room-icon me-3 icon-finished">
                    <i class="fa-solid fa-flag-checkered"></i>
                  </div>
                  <div class="flex-grow-1 min-w-0">
                    <div class="room-name fw-bold">{{ room.name }}</div>
                    <div class="room-meta">{{ formatDateShort(room.created_at) }}</div>
                  </div>
                  <span class="room-badge ms-2 badge-finished">Завершена</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <button @click="showLogoutModal = true" class="btn w-100 logout-bottom-btn mb-4">
          <i class="fa-solid fa-right-from-bracket me-2"></i>
          Вийти з акаунту
        </button>

        <div v-if="showLogoutModal" class="custom-modal-overlay d-flex align-items-center justify-content-center z-3">
          <div class="glass-box modal-card p-4 text-center mx-3 fade-in">
            <div class="warning-icon-wrapper mx-auto mb-3">
              <i class="fa-solid fa-right-from-bracket text-danger fs-1"></i>
            </div>
            <h4 class="fw-bold mb-2" style="color: #3b1c1c;">Вийти з акаунту?</h4>
            <p class="text-muted mb-4 small">
              Доведеться знову вводити логін та пароль при наступному вході.
            </p>
            <div class="d-flex gap-3">
              <button class="btn create-btn flex-fill" @click="showLogoutModal = false">Скасувати</button>
              <button class="btn btn-danger flex-fill fw-bold" style="border-radius: 12px;" @click="confirmLogout">Вийти</button>
            </div>
          </div>
        </div>

        <div v-if="showEditModal" class="custom-modal-overlay d-flex align-items-center justify-content-center z-3" @click.self="closeEditModal">
          <div class="glass-box edit-modal-card p-4 mx-3 fade-in">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h5 class="fw-bold mb-0" style="color: #3b1c1c;">Редагування профілю</h5>
              <button class="btn-close-modal" @click="closeEditModal">
                <i class="fa-solid fa-xmark"></i>
              </button>
            </div>

            <div class="edit-tabs d-flex mb-4">
              <button
                class="edit-tab-btn flex-fill"
                :class="{ active: editTab === 'info' }"
                @click="editTab = 'info'"
              >
                <i class="fa-solid fa-user me-2"></i>Дані
              </button>
              <button
                class="edit-tab-btn flex-fill"
                :class="{ active: editTab === 'password' }"
                @click="editTab = 'password'"
                :disabled="isGoogleLinked && !user?.password_hash"
              >
                <i class="fa-solid fa-lock me-2"></i>Пароль
              </button>
            </div>

            <div v-if="editTab === 'info'">
              <div class="mb-3">
                <label class="edit-field-label">Ім'я</label>
                <input
                  v-model="editName"
                  type="text"
                  class="form-control edit-input"
                  placeholder="Ваше ім'я"
                />
              </div>
              <div class="mb-4">
                <label class="edit-field-label">Email</label>
                <input
                  v-model="editEmail"
                  type="email"
                  class="form-control edit-input"
                  placeholder="email@example.com"
                />
              </div>

              <div v-if="editError" class="alert-inline alert-inline-danger mb-3">
                <i class="fa-solid fa-circle-exclamation me-2"></i>{{ editError }}
              </div>
              <div v-if="editSuccess" class="alert-inline alert-inline-success mb-3">
                <i class="fa-solid fa-check-circle me-2"></i>{{ editSuccess }}
              </div>

              <div class="d-flex gap-3">
                <button class="btn create-btn flex-fill" @click="closeEditModal">Скасувати</button>
                <button class="btn save-btn flex-fill" @click="saveProfile" :disabled="editLoading">
                  <span v-if="editLoading" class="spinner-border spinner-border-sm me-2"></span>
                  Зберегти
                </button>
              </div>
            </div>

            <div v-if="editTab === 'password'">
              <div v-if="isGoogleLinked && !user?.hasPassword" class="alert-inline alert-inline-danger mb-3">
                <i class="fa-solid fa-circle-info me-2"></i>Google-акаунти не мають пароля
              </div>
              <template v-else>
                <div class="mb-3">
                  <label class="edit-field-label">Поточний пароль</label>
                  <input
                    v-model="currentPassword"
                    type="password"
                    class="form-control edit-input"
                    placeholder="••••••••"
                  />
                </div>
                <div class="mb-3">
                  <label class="edit-field-label">Новий пароль</label>
                  <input
                    v-model="newPassword"
                    type="password"
                    class="form-control edit-input"
                    placeholder="Введіть новий пароль"
                  />
                </div>
                <div class="mb-4">
                  <label class="edit-field-label">Підтвердження</label>
                  <input
                    v-model="confirmPassword"
                    type="password"
                    class="form-control edit-input"
                    placeholder="Повторіть новий пароль"
                  />
                </div>

                <div v-if="pwdError" class="alert-inline alert-inline-danger mb-3">
                  <i class="fa-solid fa-circle-exclamation me-2"></i>{{ pwdError }}
                </div>
                <div v-if="pwdSuccess" class="alert-inline alert-inline-success mb-3">
                  <i class="fa-solid fa-check-circle me-2"></i>{{ pwdSuccess }}
                </div>

                <div class="d-flex gap-3">
                  <button class="btn create-btn flex-fill" @click="closeEditModal">Скасувати</button>
                  <button class="btn save-btn flex-fill" @click="savePassword" :disabled="pwdLoading">
                    <span v-if="pwdLoading" class="spinner-border spinner-border-sm me-2"></span>
                    Змінити
                  </button>
                </div>
              </template>
            </div>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
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
  height: 70px;
}

.mini-title { font-size: 20px; color: #ffffff; }

.back-icon {
  font-size: 18px;
  color: rgba(255,255,255,0.85);
  cursor: pointer;
  transition: color 0.2s;
}
.back-icon:hover { color: #fff; }

.edit-header-btn {
  background: rgba(255,255,255,0.15);
  color: #625050;
  opacity: 0.7;
  border: 1px solid #6250507e;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  padding: 6px 16px;
  transition: all 0.2s;
}
.edit-header-btn:hover {
  background: #62505027;
  border-color: #625050
}

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

.room-name {
  font-size: 15px; 
  color: #3b1c1c; 
  white-space: normal;
  word-wrap: break-word;
  line-height: 1.3;
}

.min-w-0 { min-width: 0; }

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

.custom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(98, 80, 80, 0.8);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  z-index: 1050;
}

.modal-card {
  max-width: 340px;
  width: 100%;
  border-radius: 24px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2);
}

.edit-modal-card {
  max-width: 380px;
  width: 100%;
  border-radius: 24px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2);
}

.btn-close-modal {
  background: rgba(98, 80, 80, 0.1);
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: #625050;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-close-modal:hover { background: rgba(98, 80, 80, 0.2); }

.edit-tabs {
  background: rgba(98, 80, 80, 0.08);
  border-radius: 12px;
  padding: 4px;
  gap: 4px;
}

.edit-tab-btn {
  background: transparent;
  border: none;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 600;
  color: #625050;
  padding: 8px 12px;
  transition: all 0.2s;
  cursor: pointer;
}
.edit-tab-btn.active {
  background: #ffffff;
  color: #292CA8;
  box-shadow: 0 2px 8px rgba(41, 44, 165, 0.12);
}
.edit-tab-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.edit-field-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #625050;
  opacity: 0.7;
  margin-bottom: 6px;
  display: block;
}

.edit-input {
  background: rgba(255,255,255,0.8) !important;
  border: 1px solid rgba(98, 80, 80, 0.2) !important;
  border-radius: 12px !important;
  font-size: 15px;
  color: #3b1c1c;
  height: 46px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.edit-input:focus {
  border-color: #292CA8 !important;
  box-shadow: 0 0 0 3px rgba(41, 44, 165, 0.1) !important;
  outline: none;
}

.save-btn {
  background: #292CA8;
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  height: 46px;
  font-size: 15px;
  transition: background 0.2s;
}
.save-btn:hover:not(:disabled) { background: #1e2080; color: #fff; }
.save-btn:disabled { opacity: 0.6; }

.btn-outline-primary{
  background: rgba(255,255,255,0.15);
  color: #292CA8;
  border: 1px solid #292CA8;
  border-radius: 12px;
  font-weight: 600;
  height: 46px;
  font-size: 14px;
  padding: 6px 16px;
  transition: all 0.2s;
}
.btn-outline-primary:hover:not(:disabled) { background: rgba(30, 32, 128, 0.204); }

.alert-inline {
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  padding: 10px 14px;
}
.alert-inline-danger {
  background: rgba(192, 57, 43, 0.08);
  color: #c0392b;
  border: 1px solid rgba(192, 57, 43, 0.2);
}
.alert-inline-success {
  background: rgba(46, 125, 50, 0.08);
  color: #2e7d32;
  border: 1px solid rgba(46, 125, 50, 0.2);
}

.warning-icon-wrapper {
  width: 64px;
  height: 64px;
  background-color: rgba(217, 48, 37, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fade-in {
  animation: fadeInModal 0.2s ease-out forwards;
}

@keyframes fadeInModal {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.create-btn {
  background-color: rgba(255, 255, 255, 0.8);
  color: #625050;
  border: 1px solid #6250507e;
  border-radius: 10px;
  font-weight: 600;
  height: 46px;
  transition: all 0.2s ease;
}

.create-btn:hover {
  background-color: #62505027;
  border-color: #625050;
}
</style>