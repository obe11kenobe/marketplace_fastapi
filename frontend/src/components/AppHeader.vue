<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '../cart'
import { useAuth } from '../auth'
import { notify } from '../toast'

const cart = useCart()
const auth = useAuth()
const router = useRouter()
const menuOpen = ref(false)

function logout() {
  auth.logout()
  menuOpen.value = false
  notify('Вы вышли из аккаунта')
  router.push('/')
}
</script>

<template>
  <header class="header">
    <div class="container inner">
      <RouterLink to="/" class="logo">
        <span class="mark" aria-hidden="true"></span>
        Маркетплейс
      </RouterLink>

      <nav class="actions">
        <RouterLink to="/cart" class="icon-link" :aria-label="`Корзина, товаров: ${cart.count.value}`">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
               stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="9" cy="20" r="1.4" />
            <circle cx="18" cy="20" r="1.4" />
            <path d="M2 3h3l2.6 12.3a1.5 1.5 0 0 0 1.5 1.2h8.4a1.5 1.5 0 0 0 1.5-1.2L21 7H6" />
          </svg>
          <span class="label">Корзина</span>
          <span v-if="cart.count.value" class="count">{{ cart.count.value }}</span>
        </RouterLink>

        <template v-if="auth.isAuthenticated.value">
          <div class="menu-wrap">
            <button class="icon-link" @click="menuOpen = !menuOpen" :aria-expanded="menuOpen">
              <span class="avatar" aria-hidden="true">{{ auth.user.value.email[0].toUpperCase() }}</span>
              <span class="label email">{{ auth.user.value.email }}</span>
            </button>

            <Transition name="fade">
              <div v-if="menuOpen" class="menu card" @click="menuOpen = false">
                <RouterLink to="/orders" class="menu-item">Мои заказы</RouterLink>
                <button class="menu-item danger" @click="logout">Выйти</button>
              </div>
            </Transition>
          </div>
        </template>

        <RouterLink v-else to="/login" class="btn">Войти</RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 20;
  background: color-mix(in srgb, var(--bg-elevated) 82%, transparent);
  backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid var(--border);
}

.inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: var(--header-h);
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 16.5px;
  font-weight: 660;
  letter-spacing: -0.02em;
}

.mark {
  width: 22px;
  height: 22px;
  border-radius: 7px;
  background: linear-gradient(135deg, var(--accent), #8b5cf6);
}

.actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  font-weight: 500;
  transition: background 0.15s ease;
}

.icon-link:hover {
  background: var(--bg);
}

.count {
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 999px;
  background: var(--accent);
  color: #fff;
  font-size: 11.5px;
  font-weight: 700;
  display: grid;
  place-items: center;
}

.avatar {
  width: 26px;
  height: 26px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent), #8b5cf6);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: grid;
  place-items: center;
}

.email {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-wrap {
  position: relative;
}

.menu {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  min-width: 180px;
  padding: 6px;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
}

.menu-item {
  padding: 9px 12px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  text-align: left;
  font-size: 14px;
}

.menu-item:hover {
  background: var(--bg);
}

.menu-item.danger {
  color: var(--danger);
}

@media (max-width: 620px) {
  .label {
    display: none;
  }
}
</style>
