<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// TODO - replace with actual user data from store
const userName = ref('Хіхі хахаік'); 

// TODO - replace with actual room status from store (check if user has active room or not)
const hasActiveRoom = ref(true);
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
            <div class="avatar-circle">
                <i class="fa-solid fa-user text-white"></i>
            </div>
        </header>

        <div class="flex-grow-1 d-flex align-items-center justify-content-center p-4 position-relative z-2">
            <div class="lobby-content w-100">
                <div v-if="hasActiveRoom" class="glass-box active-trip-banner p-3 mb-4 d-flex justify-content-between align-items-center z-2">
                    <div class="d-flex align-items-center">
                        <div class="banner-icon me-3">
                            <i class="fa-solid fa-route text-white"></i>
                        </div>
                        <div>
                            <h6 class="fw-bold mb-0 text-dark-brown">У тебе є активна прогулянка!</h6>
                            <p class="text-muted small mb-0">Прогулянка Подолом</p>
                        </div>
                    </div>
                    <button @click="router.push('/room')" class="btn brown-btn btn-sm px-3">
                        Повернутися
                    </button>
                </div>
                
                <section class="welcome-section text-center mb-4">
                    <h1 class="fw-bold greeting-text mb-2">Привіт, {{ userName }}!</h1>
                </section>

                <div class="glass-card mb-4 text-start mx-auto">
                    <div class="form-wrapper mx-auto">
                        <h3 class="glass-card-title text-center mb-4">Куди вирушаємо сьогодні?</h3>
                        <input type="text" class="form-control pretty-input mb-4 text-center" placeholder="Введіть код кімнати">
                        <button @click="router.push('/room')" class="btn brown-btn w-100">Приєднатися</button>
                    </div>
                </div>

                <div class="divider mb-4 mx-auto">
                    <span>або</span>
                </div>

                <button @click="router.push('/room')" class="btn w-100 create-btn mx-auto d-block">
                    <i class="fa-solid fa-plus me-2"></i> Створити кімнату
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

.mini-logo { 
    height: 35px; 
}

.mini-title {
    font-size: 20px; 
    color: #ffffff; 
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

.lobby-content {
    width: 100%;
    max-width: 400px;
}

.greeting-text { 
    font-size: 30px; 
    color: #292CA8;
}

.subtitle {
    color: #646dd2; 
    opacity: 0.9; 
    font-size: 16px;
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
    margin-top: 35px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
}

.form-wrapper {
    max-width: 320px; 
}

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

.brown-btn {
    background-color: #625050;
    color: #ffffff;
    border: none;
    height: 48px;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
}
.brown-btn:hover { background-color: #4a3c3c; }

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

.divider span {
    padding: 0 15px; 
    font-size: 14px; 
}

.text-dark-brown {
    color: #3b1c1c;
}

.active-trip-banner {
    border-left: 5px solid #292CA8;
    width: 100%;
}

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
</style>