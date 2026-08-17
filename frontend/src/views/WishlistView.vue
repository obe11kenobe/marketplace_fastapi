<script setup>
import { onMounted, ref } from 'vue'
import ProductCard from '../components/ProductCard.vue'
import { useWishlist } from '../wishlist'

const wishlist = useWishlist()
const loading = ref(true)

onMounted(async () => {
  await wishlist.load()
  loading.value = false
})
</script>

<template>
  <header class="head">
    <h1>Избранное</h1>
    <span v-if="wishlist.count.value" class="muted">{{ wishlist.count.value }}</span>
  </header>

  <p v-if="wishlist.error.value" class="alert">{{ wishlist.error.value }}</p>

  <div v-else-if="loading" class="grid">
    <div v-for="n in 3" :key="n" class="card sk-card">
      <div class="skeleton sk-thumb" />
      <div class="skeleton sk-line" />
      <div class="skeleton sk-line short" />
    </div>
  </div>

  <div v-else-if="!wishlist.count.value" class="empty">
    <p class="muted">В избранном пока ничего нет. Нажмите сердечко на карточке товара.</p>
    <RouterLink to="/" class="btn">В каталог</RouterLink>
  </div>

  <div v-else class="grid">
    <ProductCard v-for="f in wishlist.items.value" :key="f.id" :product="f.product" />
  </div>
</template>

<style scoped>
.head {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 24px;
}

h1 {
  font-size: 26px;
  margin: 0;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 18px;
}

.empty {
  padding: 64px 0;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}
</style>
