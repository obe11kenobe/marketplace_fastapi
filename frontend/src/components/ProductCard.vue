<script setup>
import { useRouter } from 'vue-router'
import { useCart } from '../cart'
import { useAuth } from '../auth'
import { useWishlist } from '../wishlist'
import { notify } from '../toast'

const props = defineProps({
  product: { type: Object, required: true },
})

const cart = useCart()
const auth = useAuth()
const wishlist = useWishlist()
const router = useRouter()

const money = (n) => n.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

async function add() {
  await cart.add(props.product.id)
  notify(`«${props.product.name}» в корзине`)
}

async function toggleFavorite() {
  if (!auth.isAuthenticated.value) {
    notify('Войдите, чтобы добавлять в избранное', 'error')
    return router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
  }
  try {
    const added = await wishlist.toggle(props.product.id)
    notify(added ? `«${props.product.name}» в избранном` : `«${props.product.name}» убран из избранного`)
  } catch (e) {
    notify(e.message, 'error')
  }
}
</script>

<template>
  <article class="card product">
    <div class="media">
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

      <button class="fav" :class="{ active: wishlist.has(product.id) }" @click="toggleFavorite"
              :aria-label="wishlist.has(product.id) ? 'Убрать из избранного' : 'В избранное'"
              :aria-pressed="wishlist.has(product.id)">
        <svg width="18" height="18" viewBox="0 0 24 24" :fill="wishlist.has(product.id) ? 'currentColor' : 'none'"
             stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
             aria-hidden="true">
          <path d="M20.8 5.6a5 5 0 0 0-7.1 0L12 7.3l-1.7-1.7a5 5 0 0 0-7.1 7.1l8.1 8.1a1 1 0 0 0 1.4 0l8.1-8.1a5 5 0 0 0 0-7.1z" />
        </svg>
      </button>
    </div>

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

.media {
  position: relative;
}

.thumb {
  display: block;
  aspect-ratio: 4 / 3;
  background: var(--bg);
  overflow: hidden;
}

.fav {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: color-mix(in srgb, var(--surface) 88%, transparent);
  backdrop-filter: blur(6px);
  color: var(--muted);
  transition: color 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
}

.fav:hover {
  color: var(--danger);
  border-color: var(--border-strong);
  transform: scale(1.08);
}

.fav.active {
  color: var(--danger);
  border-color: color-mix(in srgb, var(--danger) 35%, var(--border));
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
