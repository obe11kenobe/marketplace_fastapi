<script setup>
import { onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import { useCart } from './cart'

const cart = useCart()

onMounted(cart.sync)
</script>

<template>
  <AppHeader />
  <main class="container page">
    <RouterView />
  </main>
</template>

<style scoped>
.page {
  padding-top: 28px;
  padding-bottom: 64px;
}
</style>
