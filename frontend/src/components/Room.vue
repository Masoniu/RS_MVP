<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { roomsApi } from '../api/rooms';
import { expensesApi } from '../api/expenses';
import LocationCards from '../components/LocationCards.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const roomId = computed(() => parseInt(route.params.id));

const room = ref(null);
const members = ref([]);
const loading = ref(true);
const error = ref('');

const currentUserId = computed(() => authStore.user?.id);
const isHost = computed(() => room.value?.creator_id === currentUserId.value);
const isFinished = computed(() => room.value?.status === 'finished');
const roomCode = computed(() => room.value?.invite_code || '');

const expenses = ref([]);
const balances = ref({});
const settlements = ref([]);
const expensesLoading = ref(false);

const showExpenseForm = ref(false);
const newExpense = ref({ description: '', amount: '', payerId: '', splitBetween: [] });
const expenseError = ref('');
const expenseSubmitting = ref(false);

const routeData = ref(null);
const routeLoading = ref(false);
const routeError = ref('');
const isSwiping = ref(false);

const startSwipe = (event) => {
    isSwiping.value = true;
};

const budgetOptions = [
  { label: 'До 500 грн', value: 500 },
  { label: 'До 1000 грн', value: 1000 },
  { label: 'До 10 000 грн', value: 10000 },
];
const radiusOptions = [
  { label: 'Пішки (2 км)', value: 2 },
  { label: 'Середній (5 км)', value: 5 },
  { label: 'На таксі (20 км)', value: 20 },
];
const selectedBudget = ref(500);
const selectedRadius = ref(2);
const userLat = ref(null);
const userLon = ref(null);

//current tab in room page (map, participants, expenses) - for me to check
const activeTab = ref('expenses');
//DO NOT TOUCH HEADER AND SCROLL, THESE ARE MINE >:)
const showHeader = ref(true);
let lastScrollPosition = 0;

const handleScroll = () => {
    const currentScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    if (currentScrollPosition <= 0) {
        showHeader.value = true;
        return;
    }

    if (Math.abs(currentScrollPosition - lastScrollPosition) < 50) {
        return; 
    }

    showHeader.value = currentScrollPosition < lastScrollPosition;
    
    lastScrollPosition = currentScrollPosition;
};

onMounted(async () => {
    window.addEventListener('scroll', handleScroll);
    await loadRoom();

    navigator.geolocation?.getCurrentPosition(
        (pos) => { userLat.value = pos.coords.latitude; userLon.value = pos.coords.longitude; },
        () => {}
    );
});

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll);
});

async function loadRoom() {
  loading.value = true;
  error.value = '';
  try {
    const { data } = await roomsApi.getRoom(roomId.value);
    room.value = data;
    members.value = data.members || [];
    await loadExpensesAndBalances();
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не вдалося завантажити кімнату';
  } finally {
    loading.value = false;
  }
}

async function loadExpensesAndBalances() {
  expensesLoading.value = true;
  try {
    const [expRes, balRes] = await Promise.all([
      expensesApi.getExpenses(roomId.value),
      roomsApi.getBalances(roomId.value),
    ]);
    expenses.value = expRes.data;
    balances.value = balRes.data.balances || {};

    if (isFinished.value) {
      const { data } = await roomsApi.getSettlements(roomId.value);
      settlements.value = data;
    }
  } catch {} 
    finally {
    expensesLoading.value = false;
  }
}

async function generateRoute() {
  routeLoading.value = true;
  routeError.value = '';
  try {
    // await roomsApi.generateRoute(roomId.value, { budget: selectedBudget.value, radius: selectedRadius.value, lat: userLat.value, lon: userLon.value });
    setTimeout(() => {
        isSwiping.value = true;
        routeLoading.value = false;
    }, 800);
  } catch (err) {
    routeError.value = err.response?.data?.detail || 'Помилка при генерації маршруту';
    routeLoading.value = false;
  }
}

const totalExpenses = computed(() =>
  expenses.value.reduce((sum, e) => sum + e.amount, 0)
);

function getMemberName(userId) {
  const m = members.value.find((m) => m.id === userId);
  return m ? m.name : `Користувач ${userId}`;
}

function resetExpenseForm() {
  newExpense.value = {
    description: '',
    amount: '',
    payerId: currentUserId.value || '',
    splitBetween: members.value.map((m) => m.id),
  };
  expenseError.value = '';
}

function openExpenseForm() {
  resetExpenseForm();
  showExpenseForm.value = true;
}

async function submitExpense() {
  expenseError.value = '';
  if (!newExpense.value.description || !newExpense.value.amount) {
    expenseError.value = 'Заповніть опис та суму';
    return;
  }
  if (!newExpense.value.splitBetween.length) {
    expenseError.value = 'Оберіть хоч одного учасника';
    return;
  }
  expenseSubmitting.value = true;
  try {
    await expensesApi.createExpense({
      roomId: roomId.value,
      payerId: parseInt(newExpense.value.payerId),
      amount: parseFloat(newExpense.value.amount),
      description: newExpense.value.description,
      splitBetween: newExpense.value.splitBetween.map(Number),
    });
    showExpenseForm.value = false;
    await loadExpensesAndBalances();
  } catch (err) {
    expenseError.value = err.response?.data?.detail || 'Помилка при додаванні витрати';
  } finally {
    expenseSubmitting.value = false;
  }
}

function toggleSplitMember(memberId) {
  const idx = newExpense.value.splitBetween.indexOf(memberId);
  if (idx === -1) newExpense.value.splitBetween.push(memberId);
  else newExpense.value.splitBetween.splice(idx, 1);
}

async function finishRoom() {
  if (!confirm('Завершити прогулянку? Це не можна відмінити.')) return;
  try {
    await roomsApi.finishRoom(roomId.value);
    localStorage.removeItem('active_room_id');
    room.value.status = 'finished';
    await loadExpensesAndBalances();
  } catch (err) {
    alert(err.response?.data?.detail || 'Помилка');
  }
}

const leaveRoom = () => {
    localStorage.removeItem('active_room_id');
    router.push('/lobby');
};

const copyCode = () => {
    navigator.clipboard.writeText(roomCode.value);
    console.log('Код скопійовано!');
};
</script>

<template>
    <div class="room-page d-flex flex-column min-vh-100">
        <div class="map-pillar pillar-left d-none d-lg-block"></div>
        <div class="map-pillar pillar-right d-none d-lg-block"></div>

        <header class="room-header d-flex align-items-center justify-content-between px-4 py-3 z-3" :class="{'header-hidden': !showHeader}">
            <div class="d-flex align-items-center header-side">
                <i class="fa-solid fa-chevron-left back-icon me-3" @click="leaveRoom"></i>
                <h2 class="fw-bold m-0 room-title text-truncate">{{ room?.name || 'Кімната' }}</h2>
            </div>

            <nav class="desktop-nav d-none d-md-flex align-items-center justify-content-center">
                <div class="desktop-nav-item" :class="{ active: activeTab === 'map' }" @click="activeTab = 'map'">Мапа</div>
                <div class="desktop-nav-item" :class="{ active: activeTab === 'participants' }" @click="activeTab = 'participants'">Учасники</div>
                <div class="desktop-nav-item" :class="{ active: activeTab === 'expenses' }" @click="activeTab = 'expenses'">Витрати</div>
            </nav>

            <div class="d-flex justify-content-end header-side">
                <div class="avatar-circle">
                    <i class="fa-solid fa-user text-white"></i>
                </div>
            </div>
        </header>

        <main class="flex-grow-1 px-4 main-content z-2">
            <div class="content-wrapper mx-auto" :style="activeTab === 'map' ? 'max-width: 1100px;' : 'max-width: 600px;'">

                <div v-if="loading" class="text-center py-5">
                    <div class="spinner-border text-primary"></div>
                </div>

                <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

                <template v-else>
                    <div v-if="activeTab !== 'map'" class="mb-4">
                        <p class="section-title mb-3">Код запрошення</p>
                        <div class="glass-box d-flex justify-content-between align-items-center px-4 py-3">
                            <span class="room-code fw-bold">{{ roomCode.split('').join(' ') }}</span>
                            <button class="btn copy-btn" @click="copyCode" title="Скопіювати">
                                <i class="fa-solid fa-copy"></i>
                            </button>
                        </div>
                    </div>

                    <div v-if="activeTab !== 'map'" class="section-divider my-4"></div>

                    <div v-if="activeTab === 'participants'" class="participants-section">
                        <p class="section-title mb-3">Учасники ({{ members.length }})</p>

                        <div
                            v-for="member in members"
                            :key="member.id"
                            class="glass-box participant-card d-flex align-items-center mb-3 px-3 py-2"
                        >
                            <div class="avatar-circle me-3"><i class="fa-solid fa-user text-white"></i></div>
                            <span class="participant-name flex-grow-1 fw-bold">{{ member.name }}</span>
                            <span v-if="member.id === room.creator_id" class="badge host-badge">хост</span>
                            <span v-if="member.id === currentUserId" class="badge you-badge">Ви</span>
                        </div>
                    </div>

                    <div v-if="activeTab === 'expenses'" class="expenses-section">

                        <div v-if="!isFinished">
                            <div class="mb-4">
                                <p class="section-title mb-2">Витрати</p>
                                <div class="glass-box d-flex justify-content-between align-items-center px-4 py-3">
                                    <div>
                                        <h3 class="expense-total fw-bold mb-0">{{ totalExpenses.toFixed(0) }} грн</h3>
                                        <span class="expense-subtitle">{{ expenses.length }} транзакцій</span>
                                    </div>
                                    <button class="btn add-expense-btn" @click="openExpenseForm">
                                        <i class="fa-solid fa-plus"></i>
                                    </button>
                                </div>
                            </div>

                            <div v-if="showExpenseForm" class="glass-box p-4 mb-4">
                                <h6 class="fw-bold mb-3" style="color: #3b1c1c;">Нова витрата</h6>

                                <input v-model="newExpense.description" type="text" class="form-control pretty-input mb-2" placeholder="Опис (напр. Квитки)">
                                <input v-model="newExpense.amount" type="number" min="0" class="form-control pretty-input mb-3" placeholder="Сума (грн)">

                                <label class="form-label text-muted small mb-1">Хто платив</label>
                                <select v-model="newExpense.payerId" class="form-select custom-select mb-3">
                                    <option v-for="m in members" :key="m.id" :value="m.id">{{ m.name }}</option>
                                </select>

                                <label class="form-label text-muted small mb-2">Ділять між:</label>
                                <div class="d-flex flex-wrap gap-2 mb-3">
                                    <button
                                        v-for="m in members"
                                        :key="m.id"
                                        type="button"
                                        class="btn btn-sm split-toggle"
                                        :class="newExpense.splitBetween.includes(m.id) ? 'active' : ''"
                                        @click="toggleSplitMember(m.id)"
                                    >{{ m.name }}</button>
                                </div>

                                <p v-if="expenseError" class="text-danger small mb-2">{{ expenseError }}</p>

                                <button class="btn brown-btn w-100 mb-2" @click="submitExpense" :disabled="expenseSubmitting">
                                    <span v-if="expenseSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                                    Зберегти
                                </button>
                                <button class="btn create-btn w-100" @click="showExpenseForm = false">Скасувати</button>
                            </div>

                            <div v-if="expenses.length" class="mb-4">
                                <p class="section-title mb-2">Останні витрати</p>
                                <div
                                    v-for="exp in expenses"
                                    :key="exp.id"
                                    class="glass-box participant-card d-flex align-items-center mb-2 px-3 py-2"
                                >
                                    <div class="avatar-circle me-3"><i class="fa-solid fa-receipt text-white"></i></div>
                                    <div class="flex-grow-1">
                                        <div class="fw-bold item-name">{{ exp.description }}</div>
                                        <div class="item-details">
                                            Платив: {{ getMemberName(exp.payer_id) }} · ділять: {{ exp.splits.length }} чол.
                                        </div>
                                    </div>
                                    <span class="fw-bold item-amount">{{ exp.amount.toFixed(0) }} грн</span>
                                </div>
                            </div>
                            <div v-else-if="!expensesLoading" class="text-center text-muted py-3">Поки що немає витрат</div>

                            <div v-if="Object.keys(balances).length" class="mb-4">
                                <p class="section-title mb-2">Баланси</p>
                                <div
                                    v-for="(amount, userId) in balances"
                                    :key="userId"
                                    class="glass-box participant-card d-flex align-items-center mb-2 px-3 py-2"
                                >
                                    <div class="avatar-circle me-3"><i class="fa-solid fa-user text-white"></i></div>
                                    <span class="participant-name flex-grow-1 fw-bold">{{ getMemberName(parseInt(userId)) }}</span>
                                    <span class="fw-bold" :class="amount > 0 ? 'text-success' : amount < 0 ? 'text-danger' : ''">
                                        {{ amount > 0 ? '+' : '' }}{{ amount.toFixed(0) }} грн
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div v-else>
                            <div class="mb-4">
                                <p class="section-title mb-3">Фінальні розрахунки</p>
                                <div v-if="settlements.length === 0" class="text-center text-muted py-3">
                                    Всі розрахунки рівні
                                </div>
                                <div
                                    v-for="(s, i) in settlements"
                                    :key="i"
                                    class="glass-box participant-card d-flex align-items-center mb-3 px-3 py-3"
                                >
                                    <div class="avatar-circle me-3"><i class="fa-solid fa-money-bill-transfer text-white"></i></div>
                                    <span class="participant-name flex-grow-1 fw-bold">
                                        {{ getMemberName(s.from_user) }}
                                        <i class="fa-solid fa-arrow-right mx-1 text-muted"></i>
                                        {{ getMemberName(s.to_user) }}
                                    </span>
                                    <span class="fw-bold text-danger">{{ s.amount.toFixed(0) }} грн</span>
                                </div>
                            </div>
                        </div>
                    </div>

                <div v-if="activeTab === 'map'" class="d-flex flex-column flex-lg-row gap-4 align-items-start w-100">
                    
                    <div class="map-placeholder d-none d-lg-flex flex-column glass-box p-0 overflow-hidden w-100" style="flex: 1; min-height: 550px;">
                        <div class="w-100 h-100 d-flex flex-column align-items-center justify-content-center" style="background-color: rgba(98, 80, 80, 0.05); min-height: 550px;">
                            <i class="fa-solid fa-map-location-dot mb-3" style="font-size: 64px; color: #292CA8; opacity: 0.5;"></i>
                            <h4 class="fw-bold" style="color: #625050;">Мапа маршруту</h4>
                            <p class="text-muted small">Сюди потім підключимо OpenStreetMap</p>
                        </div>
                    </div>

                    <div class="controls-column w-100 d-flex flex-column" style="max-width: 450px; margin: 0 auto;">
                        
                        <div v-if="isSwiping">
                            <LocationCards />
                        </div>

                        <div v-else>
                            <div v-if="isHost && !isFinished" class="glass-box p-4 mb-4">
                                <p class="fw-bold mb-3" style="color: #3b1c1c;">Параметри прогулянки</p>

                                <div class="mb-3">
                                    <label class="form-label text-muted small mb-1">Бюджет</label>
                                    <select v-model="selectedBudget" class="form-select custom-select">
                                        <option v-for="opt in budgetOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                                    </select>
                                </div>

                                <div class="mb-4">
                                    <label class="form-label text-muted small mb-1">Радіус пошуку</label>
                                    <select v-model="selectedRadius" class="form-select custom-select">
                                        <option v-for="opt in radiusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                                    </select>
                                </div>

                                <p v-if="!userLat" class="text-warning small mb-2">
                                    <i class="fa-solid fa-triangle-exclamation me-1"></i>
                                    Дозвольте доступ до геолокації в браузері, щоб знайти локації поряд
                                </p>
                                <p v-if="routeError" class="text-danger small mb-2">{{ routeError }}</p>

                                <button class="btn brown-btn w-100" @click="generateRoute" :disabled="routeLoading || !userLat">
                                    <span v-if="routeLoading" class="spinner-border spinner-border-sm me-2"></span>
                                    Знайти локації
                                </button>
                            </div>

                            <div v-else-if="!isHost" class="glass-box p-4 text-center mb-4">
                                    <div class="mb-3">
                                        <i class="fa-solid fa-compass fa-spin fs-1" style="color: #292CA8;"></i>
                                    </div>
                                    <h5 class="fw-bold" style="color: #3b1c1c;">Очікуємо на хоста</h5>
                                    <p class="text-muted mb-0" style="font-size: 14px;">Хост зараз налаштовує параметри та радіус нашої прогулянки. Зачекайте трохи...</p>
                            </div>
                        </div>

                    </div>
                </div>

                <button v-if="isHost && !isFinished && activeTab !== 'map'" @click="finishRoom" class="btn brown-btn w-100 mt-4 mb-4">
                    Завершити прогулянку
                </button>
                <div v-if="isFinished && activeTab !== 'map'" class="text-center text-muted py-3 mb-4">
                    <i class="fa-solid fa-check-circle me-2 text-success"></i>Прогулянка завершена
                </div>
                </template>
            </div>
        </main>

        <nav class="bottom-nav d-flex justify-content-around align-items-center py-2 z-3 d-md-none">
            <div class="nav-item" :class="{active: activeTab === 'map'}" @click="activeTab = 'map'">
                <i class="fa-solid fa-location-dot"></i>
            </div>
            <div class="nav-item" :class="{active: activeTab === 'participants'}" @click="activeTab = 'participants'">
                <i class="fa-solid fa-users"></i>
            </div>
            <div class="nav-item" :class="{active: activeTab === 'expenses'}" @click="activeTab = 'expenses'">
                <i class="fa-solid fa-wallet"></i>
            </div>
        </nav>
    </div>
</template>

<style scoped>
.room-page {
    background-color: var(--bg-main, #f8f9fa);
    background-image: 
        radial-gradient(circle at 80% 20%, rgba(100, 109, 210, 0.3) 0%, rgba(98, 80, 80, 0) 40%),
        radial-gradient(circle at 20% 80%, rgba(100, 109, 210, 0.3) 0%, rgba(100, 109, 210, 0) 45%);
    width: 100%;
    position: relative;
    background-attachment: fixed;
}

.header-side {
    flex: 1;
    min-width: 0;
}

.content-wrapper{
    width: 100%;
    transition: max-width 0.3s ease;
}

.room-header {
    background-color: #292CA8; 
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    color: #ffffff;
    position: fixed;
    top: 0;           
    left: 0;
    right: 0;
    z-index: 100;
    transition: transform 0.3s ease-in-out;
}

.header-hidden {
    transform: translateY(-100%);
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

.room-title {
    white-space: normal;
    word-wrap: break-word;
    line-height: 1.2;
    max-height: 3.6em;
    overflow: hidden;
    display: -webkit-box;
    line-clamp: 3;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}

@media (min-width: 768px) {
    .room-title {
        font-size: 20px;
    }
}

.main-content {
    padding-top: 110px;
    padding-bottom: 70px; 
}

@media (min-width: 768px) {
    .main-content {
        padding-top: 120px;
        padding-bottom: 30px; 
    }
}

.section-title {
    font-size: 18px;
    font-weight: 700;
    color: #292CA8;
    letter-spacing: -0.5px;
}

.glass-box {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 20px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
    transform: translateZ(0);
}

.room-code {
    font-size: 26px;
    letter-spacing: 4px;
    color: #625050;
}

.copy-btn {
    background-color: #625050;
    color: #ffffff;
    border: none;
    border-radius: 12px;
    width: 45px;
    height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s;
}

.copy-btn:hover, .copy-btn:active {
    background-color: #4a3c3c;
}

.section-divider {
    border-bottom: 1px solid rgba(98, 80, 80, 0.4);
}

.participant-card {
    height: 65px;
    transition: transform 0.2s ease;
}

.desktop-nav{
    gap: 40px;
}

.desktop-nav-item {
    color: rgba(255, 255, 255, 0.6);
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: color 0.2s ease;
    display: flex;
    align-items: center;
}

.desktop-nav-item:hover {
    color: rgba(255, 255, 255, 0.9);
}

.desktop-nav-item.active {
    color: #ffffff;
    position: relative;
}

.desktop-nav-item.active::after {
    content: "";
    position: absolute;
    bottom: -8px;
    left: 0;
    right: 0;
    height: 3px;
    background-color: #ffffff;
    border-radius: 2px;
}

.map-pillar {
    position: fixed;
    top: 0;
    bottom: 0;
    width: 30vw; 
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

.avatar-circle {
    width: 40px;
    height: 40px;
    background-color: rgba(98, 80, 80, 0.8);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.avatar-circle i {
    font-size: 18px;
}

.participant-name {
    font-size: 17px;
    color: #3b1c1c;
}

.host-badge {
    background-color: #625050;
    color: #ffffff;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 12px;
    font-size: 13px;
}

.you-badge {
    background-color: #292CA8;
    color: #ffffff;
    font-weight: 600;
    padding: 6px 16px;
    border-radius: 12px;
    font-size: 13px;
}

.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(248, 249, 250, 0.95) 40%, rgba(248, 249, 250, 0) 100%);
    border-top: none;
    height: 90px;
    padding-bottom: 15px; 
    box-shadow: none;
}

.nav-item {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 50px;
    height: 50px;
    border-radius: 16px;
    color: #625050;
    font-size: 24px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.nav-item.active {
    background-color: rgba(41, 44, 165, 0.1);
    color: #292CA8;
    transform: translateY(-2px);
}

.expense-total {
    color: #292CA8;
    font-size: 28px;
    letter-spacing: -0.5px;
}

.expense-subtitle {
    font-size: 14px;
    color: #625050;
    opacity: 0.8;
}

.add-expense-btn {
    background-color: #625050;
    color: #ffffff;
    border: none;
    border-radius: 14px;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    transition: all 0.2s ease;
}

.add-expense-btn:hover {
    background-color: #4a3c3c;
    transform: scale(1.05);
}

.item-name {
    font-size: 16px;
    color: #3b1c1c;
}

.item-details {
    font-size: 12px;
    color: #666;
}

.item-amount {
    font-size: 16px;
    color: #292CA8;
}

.text-danger {
    color: #d93025 !important;
}

.text-success {
    color: #188038 !important;
}

.custom-select {
    background-color: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(98, 80, 80, 0.2);
    border-radius: 12px;
    padding: 12px 15px;
    color: #3b1c1c;
    font-weight: 500;
    box-shadow: none;
    transition: border-color 0.2s ease;
}

.custom-select:focus {
    border-color: #292CA8;
    outline: none;
    box-shadow: 0 0 0 0.2rem rgba(41, 44, 165, 0.1);
}

.brown-btn {
    background-color: #625050;
    color: white;
    border-radius: 14px;
    padding: 12px;
    font-weight: 600;
    border: none;
    transition: background-color 0.2s ease;
}

.brown-btn:hover {
    background-color: #4a3c3c;
}
</style>