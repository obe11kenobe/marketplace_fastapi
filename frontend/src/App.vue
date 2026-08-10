<script setup>
import { onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppToasts from './components/AppToasts.vue'
import { useCart } from './cart'
import { useAuth } from './auth'

const cart = useCart()
const auth = useAuth()

onMounted(async () => {
  await auth.restore()
  await cart.sync()
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
