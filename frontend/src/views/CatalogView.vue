<script setup>
import { ref, watch, onMounted } from 'vue'
import { api } from '../api'
import ProductCard from '../components/ProductCard.vue'

const props = defineProps({
  categoryId: { type: Number, default: null },
})

const categories = ref([])
const products = ref([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = props.categoryId
      ? await api.productsByCategory(props.categoryId)
      : await api.products()
    products.value = data.products
  } catch (e) {
    error.value = e.message
    products.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    categories.value = await api.categories()
  } catch (e) {
    error.value = e.message
  }
  await load()
})

watch(() => props.categoryId, load)
</script>

<template>
  <section class="hero">
    <h1>Каталог</h1>
    <p class="muted">Всё в одном месте — выбирайте и заказывайте</p>
  </section>

  <div class="layout">
    <nav class="sidebar" aria-label="Категории">
      <RouterLink to="/" class="cat" :class="{ active: !categoryId }">Все товары</RouterLink>
      <RouterLink v-for="c in categories" :key="c.id"
                  :to="{ name: 'category', params: { id: c.id } }"
                  class="cat" :class="{ active: categoryId === c.id }">
        {{ c.name }}
      </RouterLink>
    </nav>

    <section>
      <p v-if="error" class="alert">{{ error }}</p>

      <div v-if="loading" class="grid">
        <div v-for="n in 6" :key="n" class="card sk-card">
          <div class="skeleton sk-thumb" />
          <div class="skeleton sk-line" />
          <div class="skeleton sk-line short" />
        </div>
      </div>

      <p v-else-if="!products.length" class="muted empty">В этой категории пока нет товаров.</p>

      <div v-else class="grid">
        <ProductCard v-for="p in products" :key="p.id" :product="p" />
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  margin-bottom: 28px;
}

.hero h1 {
  font-size: 30px;
  margin: 0 0 6px;
}

.hero p {
  margin: 0;
  font-size: 15px;
}

.layout {
  display: grid;
  grid-template-columns: 210px 1fr;
  gap: 30px;
  align-items: start;
}

@media (max-width: 780px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .cat {
    white-space: nowrap;
  }
}

.sidebar {
  position: sticky;
  top: calc(var(--header-h) + 20px);
}

.cat {
  display: block;
  padding: 9px 13px;
  border-radius: 9px;
  font-size: 14.5px;
  color: var(--text-soft);
  transition: background 0.14s ease, color 0.14s ease;
}

.cat:hover {
  background: var(--bg-elevated);
  color: var(--text);
}

.cat.active {
  background: var(--accent);
  color: #fff;
  font-weight: 550;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 22px;
}

.empty {
  padding: 64px 0;
  text-align: center;
}

.sk-card {
  padding: 0 0 18px;
  overflow: hidden;
}

.sk-thumb {
  aspect-ratio: 4 / 3;
  border-radius: 0;
}

.sk-line {
  height: 14px;
  margin: 16px 16px 0;
}

.sk-line.short {
  width: 45%;
}
</style>
