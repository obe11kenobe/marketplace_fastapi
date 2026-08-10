<script setup>
import { useCart } from '../cart'

const cart = useCart()
</script>

<template>
  <header class="header">
    <div class="container inner">
      <RouterLink to="/" class="logo">Маркетплейс</RouterLink>

      <RouterLink to="/cart" class="cart-link" :aria-label="`Корзина, товаров: ${cart.count.value}`">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
             stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="9" cy="20" r="1.5" />
          <circle cx="18" cy="20" r="1.5" />
          <path d="M2 3h3l2.6 12.3a1.5 1.5 0 0 0 1.5 1.2h8.4a1.5 1.5 0 0 0 1.5-1.2L21 7H6" />
        </svg>
        <span>Корзина</span>
        <span v-if="cart.count.value" class="badge">{{ cart.count.value }}</span>
      </RouterLink>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: color-mix(in srgb, var(--surface) 88%, transparent);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}

.inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 62px;
}

.logo {
  font-size: 17px;
  font-weight: 650;
  letter-spacing: -0.01em;
}

.cart-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-weight: 500;
}

.cart-link:hover {
  background: var(--bg);
}

.badge {
  min-width: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: var(--accent);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  line-height: 20px;
}
</style>
