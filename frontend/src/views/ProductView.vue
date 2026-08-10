<script setup>
import { ref, watch, onMounted } from 'vue'
import { api } from '../api'
import { useCart } from '../cart'
import { notify } from '../toast'

const props = defineProps({
  id: { type: Number, required: true },
})

const product = ref(null)
const loading = ref(true)
const error = ref('')
const cart = useCart()

const money = (n) => n.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

async function load() {
  loading.value = true
  error.value = ''
  try {
    product.value = await api.product(props.id)
  } catch (e) {
    error.value = e.message
    product.value = null
  } finally {
    loading.value = false
  }
}

async function add() {
  await cart.add(product.value.id)
  notify(`«${product.value.name}» в корзине`)
}

onMounted(load)
watch(() => props.id, load)
</script>

<template>
  <div v-if="loading" class="detail">
    <div class="card skeleton media" />
    <div>
      <div class="skeleton sk-line lg" />
      <div class="skeleton sk-line" />
      <div class="skeleton sk-line short" />
    </div>
  </div>

  <p v-else-if="error" class="alert">{{ error }}</p>

  <article v-else-if="product" class="detail">
    <div class="card media">
      <img v-if="product.image_url" :src="product.image_url" :alt="product.name" />
      <div v-else class="media-empty" aria-hidden="true">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
          <rect x="3" y="3" width="18" height="18" rx="3" />
          <circle cx="9" cy="9" r="1.6" />
          <path d="m3 16 4.5-4.5L14 18" />
        </svg>
      </div>
    </div>

    <div class="info">
      <RouterLink v-if="product.category"
                  :to="{ name: 'category', params: { id: product.category.id } }"
                  class="muted breadcrumb">
        ← {{ product.category.name }}
      </RouterLink>

      <h1>{{ product.name }}</h1>
      <p class="price">{{ money(product.price) }} ₽</p>
      <p class="description">{{ product.description || 'Описание пока не заполнено.' }}</p>

      <div class="actions">
        <button class="btn btn-lg" @click="add">В корзину</button>
        <RouterLink v-if="cart.quantityOf(product.id)" to="/cart" class="btn btn-ghost btn-lg">
          В корзине: {{ cart.quantityOf(product.id) }} шт.
        </RouterLink>
      </div>
    </div>
  </article>
</template>

<style scoped>
.detail {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 42px;
  align-items: start;
}

@media (max-width: 780px) {
  .detail {
    grid-template-columns: 1fr;
    gap: 26px;
  }
}

.media {
  overflow: hidden;
  aspect-ratio: 4 / 3;
  background: var(--bg);
}

.media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.media-empty {
  display: grid;
  place-items: center;
  height: 100%;
  color: var(--muted);
  opacity: 0.45;
}

.breadcrumb {
  font-size: 14px;
}

.breadcrumb:hover {
  color: var(--accent);
}

h1 {
  font-size: 30px;
  margin: 12px 0 14px;
}

.price {
  font-size: 26px;
  font-weight: 680;
  margin: 0 0 20px;
}

.description {
  color: var(--text-soft);
  margin: 0 0 30px;
  max-width: 52ch;
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.sk-line {
  height: 16px;
  margin-bottom: 14px;
}

.sk-line.lg {
  height: 30px;
  width: 70%;
}

.sk-line.short {
  width: 40%;
}
</style>
