<script setup>
import { useCart } from '../cart'

const cart = useCart()
</script>

<template>
  <h1>Корзина</h1>

  <p v-if="cart.error.value" class="alert">{{ cart.error.value }}</p>

  <p v-if="!cart.details.value.items.length" class="muted empty">
    Пока пусто. <RouterLink to="/" class="link">Перейти в каталог</RouterLink>
  </p>

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
          <span class="muted unit">{{ item.price.toLocaleString('ru-RU') }} ₽ за штуку</span>
        </div>

        <div class="qty">
          <button
            class="step"
            :aria-label="`Уменьшить количество: ${item.name}`"
            @click="cart.setQuantity(item.product_id, item.quantity - 1)"
          >−</button>
          <input
            type="number"
            min="1"
            :value="item.quantity"
            :aria-label="`Количество: ${item.name}`"
            @change="cart.setQuantity(item.product_id, $event.target.valueAsNumber)"
          />
          <button
            class="step"
            :aria-label="`Увеличить количество: ${item.name}`"
            @click="cart.setQuantity(item.product_id, item.quantity + 1)"
          >+</button>
        </div>

        <span class="subtotal">{{ item.subtotal.toLocaleString('ru-RU') }} ₽</span>

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
        <span>{{ cart.details.value.total.toLocaleString('ru-RU') }} ₽</span>
      </div>
      <button class="btn checkout" disabled>Оформить заказ</button>
      <p class="muted note">Оформление появится, когда на бэкенде будут заказы.</p>
      <button class="btn btn-ghost" @click="cart.clear()">Очистить корзину</button>
    </aside>
  </div>
</template>

<style scoped>
h1 {
  font-size: 26px;
  letter-spacing: -0.02em;
  margin: 0 0 24px;
}

.empty {
  padding: 48px 0;
}

.link {
  color: var(--accent);
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 24px;
  align-items: start;
}

@media (max-width: 760px) {
  .layout {
    grid-template-columns: 1fr;
  }
}

.list {
  list-style: none;
  margin: 0;
  padding: 4px 8px;
}

.row {
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr) auto auto auto;
  align-items: center;
  gap: 16px;
  padding: 14px 12px;
  border-bottom: 1px solid var(--border);
}

.row:last-child {
  border-bottom: 0;
}

@media (max-width: 560px) {
  .row {
    grid-template-columns: 56px minmax(0, 1fr) auto;
    row-gap: 10px;
  }
}

.thumb {
  width: 64px;
  height: 64px;
  border-radius: 8px;
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
  gap: 2px;
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
  border: 1px solid var(--border);
  border-radius: 9px;
  overflow: hidden;
}

.step {
  width: 32px;
  height: 34px;
  border: 0;
  background: transparent;
  color: var(--text);
  font-size: 16px;
}

.step:hover {
  background: var(--bg);
}

.qty input {
  width: 46px;
  height: 34px;
  border: 0;
  border-left: 1px solid var(--border);
  border-right: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  text-align: center;
  font: inherit;
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
  padding: 4px 8px;
  border-radius: 8px;
}

.remove:hover {
  color: var(--danger);
  background: var(--bg);
}

.summary {
  padding: 20px;
  position: sticky;
  top: 86px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.line {
  display: flex;
  justify-content: space-between;
}

.total {
  font-size: 18px;
  font-weight: 650;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.checkout {
  width: 100%;
  margin-top: 4px;
}

.note {
  font-size: 12px;
  margin: 0;
  text-align: center;
}
</style>
