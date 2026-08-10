<script setup>
import { useCart } from '../cart'

defineProps({
  product: { type: Object, required: true },
})

const cart = useCart()
</script>

<template>
  <article class="card product">
    <RouterLink :to="{ name: 'product', params: { id: product.id } }" class="thumb">
      <img v-if="product.image_url" :src="product.image_url" :alt="product.name" loading="lazy" />
      <div v-else class="thumb-empty" aria-hidden="true">Нет фото</div>
    </RouterLink>

    <div class="body">
      <RouterLink :to="{ name: 'product', params: { id: product.id } }" class="name">
        {{ product.name }}
      </RouterLink>
      <p v-if="product.category" class="muted category">{{ product.category.name }}</p>

      <div class="footer">
        <span class="price">{{ product.price.toLocaleString('ru-RU') }} ₽</span>
        <button class="btn" @click="cart.add(product.id)">
          {{ cart.quantityOf(product.id) ? 'Ещё' : 'В корзину' }}
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
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.product:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 24, 40, 0.1);
}

.thumb {
  aspect-ratio: 4 / 3;
  background: var(--bg);
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-empty {
  display: grid;
  place-items: center;
  height: 100%;
  color: var(--muted);
  font-size: 13px;
}

.body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 16px 16px;
  flex: 1;
}

.name {
  font-weight: 550;
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
  padding-top: 12px;
}

.price {
  font-size: 17px;
  font-weight: 650;
  white-space: nowrap;
}
</style>
