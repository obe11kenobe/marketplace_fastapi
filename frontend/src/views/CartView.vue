<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '../cart'
import { useAuth } from '../auth'
import { api } from '../api'
import { notify } from '../toast'

const cart = useCart()
const auth = useAuth()
const router = useRouter()

const placing = ref(false)
const error = ref('')

const money = (n) => n.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

async function checkout() {
  if (!auth.isAuthenticated.value) {
    router.push({ name: 'login', query: { redirect: '/cart' } })
    return
  }

  placing.value = true
  error.value = ''
  try {
    const order = await api.createOrder(cart.items)
    await cart.clear()
    notify(`Заказ №${order.id} оформлен`)
    router.push('/orders')
  } catch (e) {
    error.value = e.message
  } finally {
    placing.value = false
  }
}
</script>

<template>
  <h1>Корзина</h1>

  <p v-if="cart.error.value" class="alert">{{ cart.error.value }}</p>
  <p v-if="error" class="alert">{{ error }}</p>

  <div v-if="!cart.details.value.items.length" class="empty">
    <p class="muted">Пока пусто.</p>
    <RouterLink to="/" class="btn">Перейти в каталог</RouterLink>
  </div>

  <div v-else class="layout">
    <ul class="card list">
      <li v-for="item in cart.details.value.items" :key="item.product_id" class="row">
        <RouterLink :to="{ name: 'product', params: { id: item.product_id } }" class="thumb">
          <img v-if="item.image_url" :src="item.image_url" :alt="item.name" />
          <span v-else class="thumb-empty" aria-hidden="true" />
        </RouterLink>

        <div class="meta">
          <RouterLink :to="{ name: 'product', params: { id: item.product_id } }" class="name">
            {{ item.name }}
          </RouterLink>
          <span class="muted unit">{{ money(item.price) }} ₽ за штуку</span>
        </div>

        <div class="qty">
          <button class="step" :aria-label="`Уменьшить: ${item.name}`"
                  @click="cart.setQuantity(item.product_id, item.quantity - 1)">−</button>
          <input type="number" min="1" :value="item.quantity" :aria-label="`Количество: ${item.name}`"
                 @change="cart.setQuantity(item.product_id, $event.target.valueAsNumber)" />
          <button class="step" :aria-label="`Увеличить: ${item.name}`"
                  @click="cart.setQuantity(item.product_id, item.quantity + 1)">+</button>
        </div>

        <span class="subtotal">{{ money(item.subtotal) }} ₽</span>

        <button class="remove" :aria-label="`Удалить ${item.name}`" @click="cart.remove(item.product_id)">
          ×
        </button>
      </li>
    </ul>

    <aside class="card summary">
      <div class="line">
        <span class="muted">Товаров</span>
        <span>{{ cart.details.value.items_count }} шт.</span>
      </div>
      <div class="line total">
        <span>Итого</span>
        <span>{{ money(cart.details.value.total) }} ₽</span>
      </div>

      <button class="btn btn-lg btn-block" :disabled="placing" @click="checkout">
        {{ placing ? 'Оформляем…' : auth.isAuthenticated.value ? 'Оформить заказ' : 'Войти и оформить' }}
      </button>

      <p v-if="!auth.isAuthenticated.value" class="hint center">
        Для оформления нужен аккаунт
      </p>

      <button class="btn btn-ghost btn-block" @click="cart.clear()">Очистить корзину</button>
    </aside>
  </div>
</template>

<style scoped>
h1 {
  font-size: 26px;
  margin: 0 0 24px;
}

.empty {
  padding: 64px 0;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 24px;
  align-items: start;
}

@media (max-width: 820px) {
  .layout {
    grid-template-columns: 1fr;
  }
}

.list {
  list-style: none;
  margin: 0;
  padding: 4px 10px;
}

.row {
  display: grid;
  grid-template-columns: 68px minmax(0, 1fr) auto auto auto;
  align-items: center;
  gap: 16px;
  padding: 16px 10px;
  border-bottom: 1px solid var(--border);
}

.row:last-child {
  border-bottom: 0;
}

@media (max-width: 560px) {
  .row {
    grid-template-columns: 56px minmax(0, 1fr) auto;
    row-gap: 12px;
  }
}

.thumb {
  width: 68px;
  height: 68px;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg);
}

.thumb img,
.thumb-empty {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.name {
  font-weight: 550;
}

.name:hover {
  color: var(--accent);
}

.unit {
  font-size: 13px;
}

.qty {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  overflow: hidden;
}

.step {
  width: 34px;
  height: 36px;
  border: 0;
  background: transparent;
  font-size: 16px;
}

.step:hover {
  background: var(--bg);
}

.qty input {
  width: 48px;
  height: 36px;
  border: 0;
  border-left: 1px solid var(--border-strong);
  border-right: 1px solid var(--border-strong);
  background: transparent;
  text-align: center;
  -moz-appearance: textfield;
}

.qty input::-webkit-outer-spin-button,
.qty input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.subtotal {
  font-weight: 650;
  white-space: nowrap;
}

.remove {
  border: 0;
  background: transparent;
  color: var(--muted);
  font-size: 20px;
  line-height: 1;
  padding: 6px 9px;
  border-radius: 8px;
}

.remove:hover {
  color: var(--danger);
  background: var(--bg);
}

.summary {
  padding: 22px;
  position: sticky;
  top: calc(var(--header-h) + 20px);
  display: flex;
  flex-direction: column;
  gap: 13px;
}

.line {
  display: flex;
  justify-content: space-between;
}

.total {
  font-size: 19px;
  font-weight: 650;
  padding-top: 13px;
  border-top: 1px solid var(--border);
}

.center {
  text-align: center;
  margin: -4px 0 0;
}
</style>
