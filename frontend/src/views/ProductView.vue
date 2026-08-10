<script setup>
import { ref, watch, onMounted } from 'vue'
import { api } from '../api'
import { useCart } from '../cart'

const props = defineProps({
  id: { type: Number, required: true },
})

const product = ref(null)
const loading = ref(true)
const error = ref('')
const cart = useCart()

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

onMounted(load)
watch(() => props.id, load)
</script>

<template>
  <p v-if="loading" class="muted">Загрузка…</p>
  <p v-else-if="error" class="alert">{{ error }}</p>

  <article v-else-if="product" class="detail">
    <div class="card media">
      <img v-if="product.image_url" :src="product.image_url" :alt="product.name" />
      <div v-else class="media-empty" aria-hidden="true">Нет фото</div>
    </div>

    <div class="info">
      <RouterLink
        v-if="product.category"
        :to="{ name: 'category', params: { id: product.category.id } }"
        class="muted breadcrumb"
      >
        ← {{ product.category.name }}
      </RouterLink>

      <h1>{{ product.name }}</h1>
      <p class="price">{{ product.price.toLocaleString('ru-RU') }} ₽</p>
      <p class="description">{{ product.description || 'Описание пока не заполнено.' }}</p>

      <div class="actions">
        <button class="btn" @click="cart.add(product.id)">В корзину</button>
        <RouterLink v-if="cart.quantityOf(product.id)" to="/cart" class="btn btn-ghost">
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
  gap: 36px;
  align-items: start;
}

@media (max-width: 760px) {
  .detail {
    grid-template-columns: 1fr;
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
}

.breadcrumb {
  font-size: 14px;
}

.breadcrumb:hover {
  color: var(--accent);
}

h1 {
  font-size: 28px;
  letter-spacing: -0.02em;
  margin: 10px 0 12px;
}

.price {
  font-size: 24px;
  font-weight: 650;
  margin: 0 0 18px;
}

.description {
  color: var(--muted);
  margin: 0 0 28px;
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
