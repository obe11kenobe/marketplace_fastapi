<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const orders = ref([])
const loading = ref(true)
const error = ref('')

const STATUS = {
  new: 'Новый',
  paid: 'Оплачен',
  shipped: 'Отправлен',
  done: 'Выполнен',
  cancelled: 'Отменён',
}

const money = (n) => n.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const formatDate = (iso) =>
  new Date(iso).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

onMounted(async () => {
  try {
    orders.value = await api.orders()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <h1>Мои заказы</h1>

  <p v-if="error" class="alert">{{ error }}</p>

  <div v-else-if="loading" class="list">
    <div v-for="n in 2" :key="n" class="card skeleton block" />
  </div>

  <div v-else-if="!orders.length" class="empty">
    <p class="muted">Заказов пока нет.</p>
    <RouterLink to="/" class="btn">В каталог</RouterLink>
  </div>

  <div v-else class="list">
    <article v-for="order in orders" :key="order.id" class="card order">
      <header class="head">
        <div>
          <h2>Заказ №{{ order.id }}</h2>
          <time class="muted date">{{ formatDate(order.created_at) }}</time>
        </div>
        <span class="badge">{{ STATUS[order.status] || order.status }}</span>
      </header>

      <ul class="items">
        <li v-for="(item, i) in order.items" :key="i">
          <RouterLink :to="{ name: 'product', params: { id: item.product_id } }" class="pid">
            Товар #{{ item.product_id }}
          </RouterLink>
          <span class="muted qty">{{ item.quantity }} × {{ money(item.price) }} ₽</span>
          <span class="sum">{{ money(item.quantity * item.price) }} ₽</span>
        </li>
      </ul>

      <footer class="foot">
        <span class="muted">Итого</span>
        <strong>{{ money(order.total) }} ₽</strong>
      </footer>
    </article>
  </div>
</template>

<style scoped>
h1 {
  font-size: 26px;
  margin: 0 0 24px;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.block {
  height: 150px;
}

.empty {
  padding: 64px 0;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

.order {
  padding: 20px 22px;
}

.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border);
}

h2 {
  font-size: 16px;
  margin: 0 0 3px;
}

.date {
  font-size: 13px;
}

.items {
  list-style: none;
  margin: 0;
  padding: 6px 0;
}

.items li {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 14px;
  align-items: center;
  padding: 9px 0;
}

.pid:hover {
  color: var(--accent);
}

.qty {
  font-size: 13.5px;
  white-space: nowrap;
}

.sum {
  font-weight: 550;
  white-space: nowrap;
  min-width: 92px;
  text-align: right;
}

.foot {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding-top: 14px;
  border-top: 1px solid var(--border);
  font-size: 17px;
}
</style>
