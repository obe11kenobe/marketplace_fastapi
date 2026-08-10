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
  <div class="layout">
    <nav class="card sidebar" aria-label="Категории">
      <RouterLink to="/" class="cat" :class="{ active: !categoryId }">Все товары</RouterLink>
      <RouterLink
        v-for="c in categories"
        :key="c.id"
        :to="{ name: 'category', params: { id: c.id } }"
        class="cat"
        :class="{ active: categoryId === c.id }"
      >
        {{ c.name }}
      </RouterLink>
    </nav>

    <section>
      <p v-if="error" class="alert">{{ error }}</p>

      <div v-if="loading" class="grid">
        <div v-for="n in 6" :key="n" class="card skeleton-card">
          <div class="skeleton thumb" />
          <div class="skeleton line" />
          <div class="skeleton line short" />
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
.layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 28px;
  align-items: start;
}

@media (max-width: 760px) {
  .layout {
    grid-template-columns: 1fr;
  }
}

.sidebar {
  padding: 8px;
  position: sticky;
  top: 86px;
}

.cat {
  display: block;
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 14px;
}

.cat:hover {
  background: var(--bg);
}

.cat.active {
  background: var(--accent);
  color: #fff;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 20px;
}

.empty {
  padding: 48px 0;
  text-align: center;
}

.skeleton-card {
  padding: 0 0 16px;
  overflow: hidden;
}

.skeleton-card .thumb {
  aspect-ratio: 4 / 3;
  border-radius: 0;
}

.skeleton-card .line {
  height: 14px;
  margin: 14px 16px 0;
}

.skeleton-card .line.short {
  width: 45%;
}
</style>
