<script setup>
import { ref } from 'vue';

const places = ref([
    { 
        id: 1, 
        name: 'Кавʼярня "Зерно"', 
        description: 'Смачна кава та десерти на Подолі',
        distance: '350 м',
        price: '₴₴'
    },
    { 
        id: 2, 
        name: 'Піцерія "Маріо"', 
        description: 'Швидко, ситно і недорого',
        distance: '1.2 км',
        price: '₴'
    },
    { 
        id: 3, 
        name: 'Ресторан "Поділ Гріль"', 
        description: 'Мʼясні страви та гарна тераса',
        distance: '850 м',
        price: '₴₴₴'
    },
    { 
        id: 4, 
        name: 'Бар "Хвильовий"', 
        description: 'Коктейлі та крафтове пиво',
        distance: '500 м',
        price: '₴₴'
    }
]);

const likedCount = ref(0);
const MAX_LIKES = 3;
const isFinished = ref(false);
const flyDirection = ref(null);

const handleChoice = (isLiked) => {
    if (places.value.length === 0 || isFinished.value || flyDirection.value) return;
    
    flyDirection.value = isLiked ? 'right' : 'left';

    setTimeout(() => {
        if (isLiked) {
            likedCount.value++;
        }

        places.value.shift();
        
        flyDirection.value = null;
        offsetX.value = 0;

        if (likedCount.value >= MAX_LIKES) {
            isFinished.value = true;
        }
    }, 300);
};

const isDragging = ref(false);
const startX = ref(0);
const offsetX = ref(0);

const startDrag = (event) => {
    if (places.value.length === 0 || isFinished.value || flyDirection.value) return;
    isDragging.value = true;
    startX.value = event.type.includes('mouse') ? event.pageX : event.touches[0].clientX;
};

const onDrag = (event) => {
    if (!isDragging.value) return;
    
    const currentX = event.type.includes('mouse') ? event.pageX : event.touches[0].clientX;
    offsetX.value = currentX - startX.value; 
};

const endDrag = () => {
    if (!isDragging.value) return;
    isDragging.value = false;
    
    const threshold = 100;

    if (offsetX.value > threshold) {
        handleChoice(true);
    } else if (offsetX.value < -threshold) {
        handleChoice(false);
    } else {
        requestAnimationFrame(() => {
            offsetX.value = 0;
        });
    }
};
</script>

<template>
    <div class="cards-container d-flex flex-column align-items-center justify-content-center min-vh-100 p-4">
        
        <div v-if="!isFinished && places.length > 0" class="likes-counter mb-4 fw-bold px-4 py-2 glass-box text-dark-brown text-center w-100" style="max-width: 400px;">
            Обрано: {{ likedCount }} / 3
        </div>

        <div v-if="places.length > 0 && !isFinished" class="cards-stack position-relative mb-4 w-100" style="max-width: 400px; height: 540px;">
            
           <div v-for="(place, index) in places.slice(0, 2)" :key="place.id" 
                 class="place-card glass-box p-3 w-100 position-absolute"
                 :class="{
                    'top-card': index === 0,
                    'back-card': index === 1,
                    'fly-left': index === 0 && flyDirection === 'left',
                    'fly-right': index === 0 && flyDirection === 'right'
                 }"
                 :style="index === 0 && isDragging ? { 
                    transform: `translateX(${offsetX}px) rotate(${offsetX * 0.05}deg)`, 
                    transition: 'none' 
                 } : {}"
                 @mousedown="index === 0 && startDrag($event)"
                 @touchstart.passive="index === 0 && startDrag($event)"
                 @mousemove="index === 0 && onDrag($event)"
                 @touchmove.passive="index === 0 && onDrag($event)"
                 @mouseup="index === 0 && endDrag()"
                 @mouseleave="index === 0 && endDrag()"
                 @touchend="index === 0 && endDrag()">
                
                <div class="image-placeholder mb-3">
                    <i class="fa-solid fa-map-location-dot text-muted fs-1"></i>
                </div>
                
                <div class="card-info">
                    <h3 class="fw-bold text-start mb-2 px-2" style="color: #292CA8;">{{ place.name }}</h3>
                    
                    <div class="d-flex align-items-center gap-3 mb-2 px-2 text-muted small fw-semibold">
                        <div class="text-success">{{ place.price }}</div>
                        <div>•</div>
                        <div class="d-flex align-items-center">
                            <i class="fa-solid fa-location-dot me-1"></i>
                            <span>{{ place.distance }}</span>
                        </div>
                    </div>

                    <p class="text-muted text-start mb-2 px-2">{{ place.description }}</p>
                </div>
            </div>
            
        </div>

        <div v-else class="text-center p-4 glass-box w-100" style="max-width: 400px;">
            <div class="mb-3">
                <i :class="isFinished ? 'fa-solid fa-check-circle text-success' : 'fa-solid fa-magnifying-glass-location text-muted'" 
                   style="font-size: 48px; transition: all 0.3s ease;"></i>
            </div>
            <h3 class="fw-bold" style="color: #625050;">
                {{ isFinished ? 'Вибір зроблено!' : 'Локації закінчилися!' }}
            </h3>
            <p class="text-muted mb-0">Очікуємо на результати збігів від інших учасників...</p>
        </div>

        <div class="controls d-flex gap-4 mt-2" v-if="places.length > 0 && !isFinished">
            <button @click="handleChoice(false)" class="btn action-btn skip-btn">
                <i class="fa-solid fa-xmark"></i>
            </button>
            <button @click="handleChoice(true)" class="btn action-btn like-btn">
                <i class="fa-solid fa-heart"></i>
            </button>
        </div>

    </div>
</template>

<style scoped>
.text-dark-brown {
    color: #3b1c1c;
}

.glass-box {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 20px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
}

.image-placeholder {
    height: 350px;
    background-color: rgba(98, 80, 80, 0.1);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.action-btn {
    width: 65px;
    height: 65px;
    border-radius: 50%;
    font-size: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: transform 0.2s ease;
}

.action-btn:active {
    transform: scale(0.9);
}

.skip-btn {
    background-color: #ffffff;
    color: #625050;
    border: 2px solid rgba(98, 80, 80, 0.2);
}

.like-btn {
    background-color: #292CA8;
    color: #ffffff;
}

.likes-counter {
    border-radius: 16px;
}

.cards-stack {
    perspective: 1000px;
}

.place-card {
    top: 0;
    left: 0;
    transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
    transform-origin: bottom center;
    user-select: none;
    -webkit-user-select: none;
}

.top-card {
    z-index: 2;
    transform: translateY(0) scale(1);
    opacity: 1;
    touch-action: none;
    cursor: grab;
}

.top-card:active {
    cursor: grabbing;
}

.back-card {
    z-index: 1;
    transform: translateY(20px) scale(0.92);
    opacity: 0.7;
}

.back-card .card-info {
    opacity: 0;
    visibility: hidden;
}

.top-card .card-info {
    opacity: 1;
    visibility: visible;
}

.top-card.fly-left {
    transform: translateX(-150%) rotate(-15deg);
    opacity: 0;
}

.top-card.fly-right {
    transform: translateX(150%) rotate(15deg);
    opacity: 0;
}

.card-info{
    transition: opacity 0.3s ease-in-out;
}
</style>