<script setup>
import { onMounted, ref } from 'vue'
import StarRating from '../components/StarRating.vue'
import { api } from '../api'
import { notify } from '../toast'

const reviews = ref([])
const loading = ref(true)
const error = ref('')
const saving = ref(null)

const formatDate = (iso) =>
  new Date(iso).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  })

async function load() {
  loading.value = true
  error.value = ''
  try {
    reviews.value = await api.moderationQueue()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function moderate(review, status) {
  saving.value = review.id
  try {
    await api.moderateReview(review.id, status)
    reviews.value = reviews.value.filter((r) => r.id !== review.id)
    notify(status === 'approved' ? 'Отзыв опубликован' : 'Отзыв отклонён')
  } catch (e) {
    notify(e.message, 'error')
  } finally {
    saving.value = null
  }
}

onMounted(load)
</script>

<template>
  <header class="head">
    <div>
      <h1>Модерация отзывов</h1>
      <p class="muted sub">Старые сверху — разбирайте с начала очереди</p>
    </div>
    <span v-if="reviews.length" class="badge">{{ reviews.length }}</span>
  </header>

  <p v-if="error" class="alert">{{ error }}</p>

  <div v-else-if="loading" class="list">
    <div v-for="n in 2" :key="n" class="card skeleton block" />
  </div>

  <p v-else-if="!reviews.length" class="muted empty">Очередь пуста — всё разобрано.</p>

  <ul v-else class="list">
    <li v-for="review in reviews" :key="review.id" class="card item">
      <div class="item-head">
        <StarRating :value="review.rating" />
        <RouterLink :to="{ name: 'product', params: { id: review.product_id } }" class="link">
          Товар #{{ review.product_id }}
        </RouterLink>
        <time class="muted date">{{ formatDate(review.created_at) }}</time>
      </div>

      <p v-if="review.text" class="text">{{ review.text }}</p>
      <p v-else class="muted text">Без комментария</p>

      <div class="actions">
        <button class="btn" :disabled="saving === review.id" @click="moderate(review, 'approved')">
          Одобрить
        </button>
        <button class="btn btn-ghost danger" :disabled="saving === review.id"
                @click="moderate(review, 'rejected')">
          Отклонить
        </button>
      </div>
    </li>
  </ul>
</template>

<style scoped>
.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

h1 {
  font-size: 26px;
  margin: 0 0 3px;
}

.sub {
  font-size: 14px;
  margin: 0;
}

.list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.block {
  height: 130px;
}

.empty {
  padding: 56px 0;
  text-align: center;
}

.item {
  padding: 18px 20px;
}

.item-head {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.link:hover {
  color: var(--accent);
}

.date {
  font-size: 13px;
}

.text {
  margin: 0 0 14px;
  line-height: 1.55;
  white-space: pre-line;
}

.actions {
  display: flex;
  gap: 8px;
}

.actions .danger {
  color: var(--danger);
}
</style>
