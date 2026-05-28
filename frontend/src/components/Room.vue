<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const isHost = ref(false); 
const isFinished = ref(false);
const roomCode = ref('S T 5 4 8 7');
const activeTab = ref('expenses');

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

onMounted(() => {
    window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll);
});

const leaveRoom = () => {
    router.push('/lobby');
};

const copyCode = () => {
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
                <h2 class="fw-bold m-0 room-title text-truncate">Прогулянка Подолом</h2>
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

            <div class="content-wrapper mx-auto">
                
                <div class="mb-4">
                    <p class="section-title mb-3">Код запрошення</p>
                    <div class="glass-box d-flex justify-content-between align-items-center px-4 py-3">
                        <span class="room-code fw-bold">{{ roomCode }}</span>
                        <button class="btn copy-btn" @click="copyCode">
                            <i class="fa-solid fa-copy"></i>
                        </button>
                    </div>
                </div>

                <div class="section-divider my-4"></div>

                <div v-if="activeTab === 'participants'" class="participants-section">
                    <p class="section-title mb-3">Учасники (3)</p>
                    
                    <div class="glass-box participant-card d-flex align-items-center mb-3 px-3 py-2">
                        <div class="avatar-circle me-3"><i class="fa-solid fa-user text-white"></i></div>
                        <span class="participant-name flex-grow-1 fw-bold">Анна</span>
                        <span class="badge host-badge">хост</span>
                    </div>

                    <div class="glass-box participant-card d-flex align-items-center mb-3 px-3 py-2">
                        <div class="avatar-circle me-3"><i class="fa-solid fa-user text-white"></i></div>
                        <span class="participant-name flex-grow-1 fw-bold">Максим</span>
                    </div>

                    <div class="glass-box participant-card d-flex align-items-center mb-3 px-3 py-2">
                        <div class="avatar-circle me-3"><i class="fa-solid fa-user text-white"></i></div>
                        <span class="participant-name flex-grow-1 fw-bold">Віка</span>
                        <span class="badge you-badge">Ви</span>
                    </div>
                </div>

                <div v-if="activeTab === 'expenses'" class="expenses-section">
    
                    <div v-if="!isFinished">
                        
                        <div class="mb-4">
                            <p class="section-title mb-2">Витрати</p>
                            <div class="glass-box d-flex justify-content-between align-items-center px-4 py-3">
                                <div>
                                    <h3 class="expense-total fw-bold mb-0">1000 грн</h3>
                                    <span class="expense-subtitle">5 транзакцій</span>
                                </div>
                                <button class="btn add-expense-btn">
                                    <i class="fa-solid fa-plus"></i>
                                </button>
                            </div>
                        </div>

                        <div class="mb-4">
                            <p class="section-title mb-2">Останні витрати</p>
                            
                            <div class="glass-box participant-card d-flex align-items-center mb-2 px-3 py-2">
                                <div class="avatar-circle me-3"><i class="fa-solid fa-receipt text-white"></i></div>
                                <div class="flex-grow-1">
                                    <div class="fw-bold item-name">Квитки в метро</div>
                                    <div class="item-details">Віка - ділять: всі</div>
                                </div>
                                <span class="fw-bold item-amount">90 грн</span>
                            </div>

                            <div class="glass-box participant-card d-flex align-items-center mb-2 px-3 py-2">
                                <div class="avatar-circle me-3"><i class="fa-solid fa-receipt text-white"></i></div>
                                <div class="flex-grow-1">
                                    <div class="fw-bold item-name">Морозиво</div>
                                    <div class="item-details">Аня - ділять: Максим, Аня</div>
                                </div>
                                <span class="fw-bold item-amount">120 грн</span>
                            </div>
                        </div>

                        <div class="mb-4">
                            <p class="section-title mb-2">Баланси</p>
                            
                            <div class="glass-box participant-card d-flex align-items-center mb-2 px-3 py-2">
                                <div class="avatar-circle me-3"><i class="fa-solid fa-user text-white"></i></div>
                                <span class="participant-name flex-grow-1 fw-bold">Анна</span>
                                <span class="fw-bold text-danger">-120 грн</span>
                            </div>

                            <div class="glass-box participant-card d-flex align-items-center mb-2 px-3 py-2">
                                <div class="avatar-circle me-3"><i class="fa-solid fa-user text-white"></i></div>
                                <span class="participant-name flex-grow-1 fw-bold">Максим</span>
                                <span class="fw-bold">0 грн</span>
                            </div>

                            <div class="glass-box participant-card d-flex align-items-center mb-2 px-3 py-2">
                                <div class="avatar-circle me-3"><i class="fa-solid fa-user text-white"></i></div>
                                <span class="participant-name flex-grow-1 fw-bold">Віка</span>
                                <span class="fw-bold text-success">+30 грн</span>
                            </div>
                        </div>

                        <button v-if="isHost" @click="isFinished = true" class="btn brown-btn w-100 mt-2 mb-4">
                            Завершити прогулянку
                        </button>

                    </div>

                <div v-else>
                    
                    <div class="mb-4">
                        <p class="section-title mb-3">Фінальні розрахунки</p>
                        
                        <div class="glass-box participant-card d-flex align-items-center mb-3 px-3 py-3">
                            <div class="avatar-circle me-3"><i class="fa-solid fa-money-bill-transfer text-white"></i></div>
                            <span class="participant-name flex-grow-1 fw-bold">Анна <i class="fa-solid fa-arrow-right mx-1 text-muted"></i> Віка</span>
                            <span class="fw-bold text-danger">80 грн</span>
                        </div>

                        <div class="glass-box participant-card d-flex align-items-center mb-3 px-3 py-3">
                            <div class="avatar-circle me-3"><i class="fa-solid fa-money-bill-transfer text-white"></i></div>
                            <span class="participant-name flex-grow-1 fw-bold">Максим <i class="fa-solid fa-arrow-right mx-1 text-muted"></i> Анна</span>
                            <span class="fw-bold text-danger">1000 грн</span>
                        </div>
                    </div>

                    <button @click="leaveRoom" class="btn create-btn w-100 mt-2 mb-4">
                        Повернутися в Лобі
                    </button>

                </div>

            </div>

                <div v-if="activeTab === 'map'" class="map-section">
                    <p class="section-title mb-3">Мапа</p>
                </div>

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
    max-width: 600px;
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
</style>