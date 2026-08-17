<script setup>
import { onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppToasts from './components/AppToasts.vue'
import { useCart } from './cart'
import { useAuth } from './auth'
import { useWishlist } from './wishlist'

const cart = useCart()
const auth = useAuth()
const wishlist = useWishlist()

onMounted(async () => {
  await auth.restore()
  await Promise.all([cart.sync(), wishlist.load()])
})
</script>

<template>
  <AppHeader />
  <main class="container page">
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </main>
  <AppToasts />
</template>

<style scoped>
.page {
  padding-top: 32px;
  padding-bottom: 72px;
  min-height: calc(100vh - var(--header-h));
}
</style>
