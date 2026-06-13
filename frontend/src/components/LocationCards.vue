<script setup>
import { ref, watch, nextTick, onBeforeUnmount, computed } from 'vue';

const props = defineProps({
    locations: { type: Array, required: true },
    remainingBudget: { type: Number, required: true },
    userLocation: { type: Object, default: null },
    previousLocations: { type: Array, default: () => [] },
    isFinished: { type: Boolean, default: false },
    isExpanding: { type: Boolean, default: false }
});

const emit = defineEmits(['choiceMade', 'askExpand']);

const likedCount = computed(() => props.previousLocations.length);

const places = ref([]);
const swipesInCurrentCycle = ref(0);

const flyDirection = ref(null);
const isDragging = ref(false);
const startX = ref(0);
const offsetX = ref(0);

let miniMapInstance = null;

const drawMiniMap = () => {
    if (places.value.length === 0 || typeof window === 'undefined' || !window.L) return;
    const place = places.value[0];

    nextTick(() => {
        const safeId = `mini-map-${place.osm_id.replace(/[^a-zA-Z0-9_-]/g, '-')}`;
        const mapEl = document.getElementById(safeId);

        if (!mapEl) return;

        if (miniMapInstance) {
            miniMapInstance.remove();
            miniMapInstance = null;
        }
        miniMapInstance = window.L.map(mapEl, {
            zoomControl: false, dragging: false, scrollWheelZoom: false,
            doubleClickZoom: false, touchZoom: false
        }).setView([place.lat, place.lon], 14);

        window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(miniMapInstance);

        const waypoints = [];

        if (props.userLocation && props.userLocation.lat) {
            waypoints.push(window.L.latLng(props.userLocation.lat, props.userLocation.lon));
        }

        props.previousLocations.forEach(loc => {
            waypoints.push(window.L.latLng(loc.lat, loc.lon));
        });

        waypoints.push(window.L.latLng(place.lat, place.lon));

        if (waypoints.length > 1) {
            window.L.Routing.control({
                waypoints: waypoints,
                router: window.L.Routing.osrmv1({ profile: 'foot' }),
                lineOptions: { styles: [{ color: '#292CA8', opacity: 0.8, weight: 5 }] },
                addWaypoints: false, routeWhileDragging: false, show: false,
                fitSelectedRoutes: true
            }).addTo(miniMapInstance);
        } else {
            window.L.marker([place.lat, place.lon]).addTo(miniMapInstance);
        }
    });
};

watch(() => props.locations, (newVal) => {
    const newItems = newVal.filter(n => !places.value.some(p => p.osm_id === n.osm_id));
    const existingItems = places.value.filter(p => newVal.some(n => n.osm_id === p.osm_id));
    places.value = [...existingItems, ...newItems];
}, { immediate: true, deep: true });

watch(() => places.value[0], () => {
    setTimeout(drawMiniMap, 150);
}, { immediate: true });

onBeforeUnmount(() => {
    if (miniMapInstance) miniMapInstance.remove();
});

const handleChoice = (isLiked) => {
    if (places.value.length === 0 || flyDirection.value || props.isFinished) return;
    const currentPlace = places.value[0];

    flyDirection.value = isLiked ? 'right' : 'left';

    setTimeout(() => {
        if (isLiked) {
            places.value.shift();
            swipesInCurrentCycle.value = 0;
            emit('choiceMade', currentPlace);
        } else {
            const skipped = places.value.shift();
            places.value.push(skipped);
            swipesInCurrentCycle.value++;

            if (swipesInCurrentCycle.value >= places.value.length && places.value.length > 0) {
                emit('askExpand');
                swipesInCurrentCycle.value = 0;
            }
        }
        flyDirection.value = null;
        offsetX.value = 0;
    }, 300);
};

const startDrag = (event) => {
    if (places.value.length === 0 || flyDirection.value) return;
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
    if (offsetX.value > threshold) handleChoice(true);
    else if (offsetX.value < -threshold) handleChoice(false);
    else requestAnimationFrame(() => offsetX.value = 0);
};
</script>

<template>
    <div class="cards-container d-flex flex-column align-items-center w-100 py-2">

        <div v-if="!isFinished && places.length > 0" class="likes-counter mb-2 fw-bold px-4 py-2 glass-box text-dark-brown text-center w-100" style="max-width: 400px;">
            Обрано: {{ likedCount }} / 3
        </div>

        <div v-if="places.length > 0 && !isFinished" class="cards-stack position-relative mb-3 w-100" style="max-width: 400px; height: 540px;">

           <div v-for="(place, index) in places.slice(0, 2)" :key="place.osm_id"
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

                <div class="image-placeholder mb-3 overflow-hidden position-relative" style="padding: 0;">
                    <div v-if="index === 0" :id="`mini-map-${place.osm_id.replace(/[^a-zA-Z0-9_-]/g, '-')}`" class="w-100 h-100"></div>
                    <i v-else class="fa-solid fa-map-location-dot text-muted fs-1"></i>
                </div>

                <div class="card-info">
                    <h3 class="fw-bold text-start mb-2 px-2" style="color: #292CA8;">{{ place.name }}</h3>

                    <div class="d-flex align-items-center gap-3 mb-2 px-2 text-muted small fw-semibold">
                        <div class="text-success">{{ place.price }} грн</div>
                        <div>•</div>
                        <div class="d-flex align-items-center">
                            <i class="fa-solid fa-layer-group me-1"></i>
                            <span v-if="place.category === 'park'">Парк</span>
                            <span v-else-if="place.category === 'museum'">Музей</span>
                            <span v-else-if="place.category === 'cafe'">Кафе</span>
                        </div>
                    </div>

                    <p class="text-muted text-start mb-2 px-2">{{ place.description || 'Чудове місце для прогулянки' }}</p>
                </div>
            </div>

        </div>

        <div v-else class="text-center p-4 glass-box w-100" style="max-width: 400px;">
    <div class="mb-3">
        <i :class="isFinished ? 'fa-solid fa-check-circle text-success' : 'fa-solid fa-magnifying-glass-location text-muted'"
           style="font-size: 48px;"></i>
    </div>
    <h3 class="fw-bold" style="color: #625050;">
        {{ isFinished ? 'Вибір зроблено!' : 'Локації закінчилися!' }}
    </h3>
    <template v-if="!isFinished && wasEmptyFromStart">
        <p class="text-muted mb-3">У цьому радіусі немає локацій цієї категорії.</p>
        <button @click="emit('expandRadius')" class="btn expand-btn" :disabled="isExpanding">
            <span v-if="isExpanding" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="fa-solid fa-expand me-2"></i>
            <span v-if="!isExpanding">Збільшити радіус пошуку</span>
            <span v-else>Шукаємо...</span>
        </button>
    </template>
    <template v-else>
        <p class="text-muted mb-0">Очікуємо на результати збігів від інших учасників...</p>
    </template>
</div>

        <div class="controls d-flex gap-4" style="margin-top: -15px; z-index: 10;" v-if="places.length > 0 && !isFinished">
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

.expand-btn {
    background-color: #292CA8;
    color: white;
    border-radius: 14px;
    padding: 10px 20px;
    font-weight: 600;
    border: none;
}
.expand-btn:hover { background-color: #1e2180; }
</style>