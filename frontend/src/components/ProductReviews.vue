<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import StarRating from './StarRating.vue'
import { api } from '../api'
import { useAuth } from '../auth'
import { notify } from '../toast'

const props = defineProps({
  productId: { type: Number, required: true },
})

const auth = useAuth()
const reviews = ref([])
const rating = ref({ average_rating: null, count: 0 })
const loading = ref(true)
const error = ref('')
const saving = ref(false)

const form = ref({ rating: 0, text: '' })
const editing = ref(false)

const STATUS = {
  pending: 'На модерации',
  rejected: 'Отклонён',
}

const myReview = computed(() =>
  auth.user.value ? reviews.value.find((r) => r.user_id === auth.user.value.id) : null,
)

const formatDate = (iso) =>
  new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [list, stats] = await Promise.all([
      api.productReviews(props.productId),
      api.productRating(props.productId),
    ])
    reviews.value = list
    rating.value = stats
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function startEdit() {
  form.value = { rating: myReview.value.rating, text: myReview.value.text || '' }
  editing.value = true
}

async function submit() {
  if (!form.value.rating) return notify('Поставьте оценку', 'error')

  saving.value = true
  try {
    if (editing.value) {
      await api.updateReview(myReview.value.id, {
        rating: form.value.rating,
        text: form.value.text || null,
      })
      notify('Отзыв изменён, он снова на модерации')
    } else {
      await api.createReview({
        product_id: props.productId,
        rating: form.value.rating,
        text: form.value.text || null,
      })
      notify('Спасибо! Отзыв появится после модерации')
    }
    editing.value = false
    form.value = { rating: 0, text: '' }
    await load()
  } catch (e) {
    notify(e.message, 'error')
  } finally {
    saving.value = false
  }
}

async function remove() {
  saving.value = true
  try {
    await api.deleteReview(myReview.value.id)
    notify('Отзыв удалён')
    await load()
  } catch (e) {
    notify(e.message, 'error')
  } finally {
    saving.value = false
  }
}

onMounted(load)
watch(() => props.productId, load)
</script>

<template>
  <section class="reviews">
    <header class="head">
      <h2>Отзывы</h2>
      <div v-if="rating.count" class="summary">
        <StarRating :value="Math.round(rating.average_rating)" />
        <strong>{{ rating.average_rating.toFixed(1) }}</strong>
        <span class="muted">· {{ rating.count }}</span>
      </div>
      <span v-else class="muted">пока нет оценок</span>
    </header>

    <p v-if="error" class="alert">{{ error }}</p>

    <div v-else-if="loading" class="skeleton block" />

    <template v-else>
      <form v-if="auth.isAuthenticated.value && (!myReview || editing)" class="card form" @submit.prevent="submit">
        <div class="field">
          <label>Ваша оценка</label>
          <StarRating :value="form.rating" editable @update:value="form.rating = $event" />
        </div>

        <div class="field">
          <label for="review-text">Комментарий</label>
          <textarea id="review-text" v-model="form.text" class="input" rows="3" maxlength="2000"
                    placeholder="Что понравилось, что нет" />
        </div>

        <div class="form-actions">
          <button class="btn" type="submit" :disabled="saving">
            {{ editing ? 'Сохранить' : 'Оставить отзыв' }}
          </button>
          <button v-if="editing" class="btn btn-ghost" type="button" @click="editing = false">
            Отмена
          </button>
          <p class="hint">Отзыв можно оставить только на купленный товар.</p>
        </div>
      </form>

      <p v-else-if="!auth.isAuthenticated.value" class="muted signin">
        <RouterLink to="/login">Войдите</RouterLink>, чтобы оставить отзыв.
      </p>

      <p v-else-if="!reviews.length" class="muted">Отзывов пока нет — будьте первым.</p>

      <ul class="list">
        <li v-for="review in reviews" :key="review.id" class="card item">
          <div class="item-head">
            <StarRating :value="review.rating" />
            <time class="muted date">{{ formatDate(review.created_at) }}</time>
            <span v-if="review.status !== 'approved'" class="badge pending">
              {{ STATUS[review.status] }}
            </span>
          </div>

          <p v-if="review.text" class="text">{{ review.text }}</p>
          <p v-else class="muted text">Без комментария</p>

          <div v-if="myReview && review.id === myReview.id" class="own-actions">
            <button class="btn btn-ghost" @click="startEdit" :disabled="saving">Изменить</button>
            <button class="btn btn-ghost danger" @click="remove" :disabled="saving">Удалить</button>
          </div>
        </li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.reviews {
  margin-top: 56px;
  padding-top: 32px;
  border-top: 1px solid var(--border);
}

.head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 22px;
}

h2 {
  font-size: 20px;
  margin: 0;
}

.summary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
}

.block {
  height: 120px;
  border-radius: var(--radius);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 22px;
  margin-bottom: 22px;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

textarea.input {
  resize: vertical;
  font: inherit;
}

.signin {
  margin-bottom: 22px;
}

.signin a {
  color: var(--accent);
}

.list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item {
  padding: 16px 20px;
}

.item-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.date {
  font-size: 13px;
}

.badge.pending {
  background: color-mix(in srgb, var(--warning) 14%, transparent);
  color: var(--warning);
}

.text {
  margin: 0;
  line-height: 1.55;
  white-space: pre-line;
}

.own-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.own-actions .danger {
  color: var(--danger);
}
</style>
