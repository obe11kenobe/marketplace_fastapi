<script setup>
import { useCart } from '../cart'
import { notify } from '../toast'

const props = defineProps({
  product: { type: Object, required: true },
})

const cart = useCart()

const money = (n) => n.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

async function add() {
  await cart.add(props.product.id)
  notify(`«${props.product.name}» в корзине`)
}
</script>

<template>
  <article class="card product">
    <RouterLink :to="{ name: 'product', params: { id: product.id } }" class="thumb">
      <img v-if="product.image_url" :src="product.image_url" :alt="product.name" loading="lazy" />
      <div v-else class="thumb-empty" aria-hidden="true">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="3" />
          <circle cx="9" cy="9" r="1.6" />
          <path d="m3 16 4.5-4.5L14 18" />
        </svg>
      </div>
    </RouterLink>

    <div class="body">
      <RouterLink :to="{ name: 'product', params: { id: product.id } }" class="name">
        {{ product.name }}
      </RouterLink>
      <p v-if="product.category" class="muted category">{{ product.category.name }}</p>

      <div class="footer">
        <span class="price">{{ money(product.price) }} ₽</span>
        <button class="btn" @click="add">
          {{ cart.quantityOf(product.id) ? `Ещё · ${cart.quantityOf(product.id)}` : 'В корзину' }}
        </button>
      </div>
    </div>
  </article>
</template>

<style scoped>
.product {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
}

.product:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow);
  border-color: var(--border-strong);
}

.thumb {
  aspect-ratio: 4 / 3;
  background: var(--bg);
  overflow: hidden;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product:hover .thumb img {
  transform: scale(1.04);
}

.thumb-empty {
  display: grid;
  place-items: center;
  height: 100%;
  color: var(--muted);
  opacity: 0.5;
}

.body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 15px 17px 17px;
  flex: 1;
}

.name {
  font-weight: 560;
  line-height: 1.35;
}

.name:hover {
  color: var(--accent);
}

.category {
  font-size: 13px;
  margin: 0;
}

.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: auto;
  padding-top: 14px;
}

.price {
  font-size: 17.5px;
  font-weight: 660;
  white-space: nowrap;
}
</style>
