<script setup>
import { ref } from 'vue';
const userName = ref('Хіхі хахаік'); 
</script>

<template>
    <div class="lobby-page d-flex flex-column min-vh-100">
        
        <header class="lobby-header d-flex justify-content-between align-items-center px-4 py-3">
            <div class="d-flex align-items-center">
                <img src="../assets/logo.svg" alt="Logo" class="mini-logo me-2">
                <h2 class="fw-bold mb-0 mini-title">RouteSplitter</h2>
            </div>
            <div class="avatar-circle">
                <i class="fa-solid fa-user text-white"></i>
            </div>
        </header>

        <div class="flex-grow-1 d-flex align-items-center justify-content-center p-4">
            <div class="lobby-content w-100">
                
                <section class="welcome-section text-center">
                    <h1 class="fw-bold greeting-text mb-2">Привіт, {{ userName }}!</h1>
                    <p class="subtitle mb-4">Куди вирушаємо сьогодні?</p>
                </section>

                <div class="glass-card mb-4 mx-auto text-start">
                    <div class="form-wrapper mx-auto">
                        <h3 class="glass-card-title mb-4 text-center">Приєднатися до кімнати</h3>
                        <input type="text" class="form-control pretty-input mb-4 text-center" placeholder="Введіть код кімнати">
                        <button class="btn brown-btn w-100">Приєднатися</button>
                    </div>
                </div>

                <div class="divider mb-4">
                    <span>або</span>
                </div>

                <button class="btn w-100 create-btn">
                    <i class="fa-solid fa-plus me-2"></i> Створити кімнату
                </button>
                
            </div>
        </div>
    </div>
</template>

<style scoped>
.lobby-page {
    min-height: 100vh;
    background-color: var(--bg-main);
    background-image: 
        radial-gradient(circle at 80% 20%, rgba(100, 109, 210, 0.4) 0%, rgba(98, 80, 80, 0) 40%),
        radial-gradient(circle at 20% 80%, rgba(100, 109, 210, 0.5) 0%, rgba(100, 109, 210, 0) 45%);
    width: 100%;
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
    max-width: 400px;
}

.greeting-text { 
    font-size: 28px; 
    color: #625050; 
}

.subtitle {
    color: #625050; 
    opacity: 0.9; 
    font-size: 16px;
}

.welcome-section {
    margin-bottom: 50px;
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

.form-wrapper {
    max-width: 320px;
}

.glass-card-title {
    font-weight: 700; 
    color: #625050; 
    font-size: 22px; 
    letter-spacing: -0.5px;
}

.pretty-input {
    background-color: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(98, 80, 80, 0.3);
    border-radius: 12px;
    height: 48px;
}

.pretty-input:focus {
    background-color: #ffffff;
    border-color: #625050;
    box-shadow: 0 0 0 2px rgba(98, 80, 80, 0.15);
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
}

.create-btn {
    background-color: #ffffff;
    color: #625050;
    border: 1px solid rgba(98, 80, 80, 0.4);
    height: 48px;
    border-radius: 12px;
    transition: all 0.3s ease;
}

.create-btn:hover { 
    background-color: rgba(255, 255, 255, 0.8); 
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
</style>