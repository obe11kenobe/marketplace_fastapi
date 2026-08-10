<script setup>
import { ref, reactive, onMounted } from 'vue'
import { api } from '../api'
import { notify } from '../toast'

const products = ref([])
const categories = ref([])
const loading = ref(true)
const error = ref('')

const formOpen = ref(false)
const editingId = ref(null)
const busy = ref(false)
const formError = ref('')

const blank = { name: '', description: '', price: '', category_id: '', image_url: '' }
const form = reactive({ ...blank })

const money = (n) => n.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

async function load() {
  loading.value = true
  try {
    const [mine, cats] = await Promise.all([api.myProducts(), api.categories()])
    products.value = mine.products
    categories.value = cats
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, blank)
  editingId.value = null
  formError.value = ''
  formOpen.value = true
}

function openEdit(product) {
  Object.assign(form, {
    name: product.name,
    description: product.description || '',
    price: product.price,
    category_id: product.category_id,
    image_url: product.image_url || '',
  })
  editingId.value = product.id
  formError.value = ''
  formOpen.value = true
}

async function submit() {
  busy.value = true
  formError.value = ''
  try {
    const payload = {
      name: form.name,
      description: form.description || null,
      price: Number(form.price),
      category_id: Number(form.category_id),
      image_url: form.image_url || null,
    }

    if (editingId.value) {
      await api.updateProduct(editingId.value, payload)
      notify('Товар обновлён')
    } else {
      await api.createProduct(payload)
      notify('Товар добавлен')
    }

    formOpen.value = false
    await load()
  } catch (e) {
    formError.value = e.message
  } finally {
    busy.value = false
  }
}

async function remove(product) {
  if (!confirm(`Удалить «${product.name}»?`)) return
  try {
    await api.deleteProduct(product.id)
    notify('Товар удалён')
    await load()
  } catch (e) {
    notify(e.message, 'error')
  }
}

onMounted(load)
</script>

<template>
  <header class="head">
    <div>
      <h1>Мои товары</h1>
      <p class="muted sub">Всё, что вы продаёте</p>
    </div>
    <button class="btn" @click="openCreate">Добавить товар</button>
  </header>

  <p v-if="error" class="alert">{{ error }}</p>

  <div v-if="loading" class="grid">
    <div v-for="n in 3" :key="n" class="card skeleton block" />
  </div>

  <div v-else-if="!products.length" class="empty card">
    <p class="muted">Товаров пока нет.</p>
    <button class="btn" @click="openCreate">Добавить первый</button>
  </div>

  <div v-else class="grid">
    <article v-for="p in products" :key="p.id" class="card item">
      <RouterLink :to="{ name: 'product', params: { id: p.id } }" class="thumb">
        <img v-if="p.image_url" :src="p.image_url" :alt="p.name" />
        <span v-else class="thumb-empty" aria-hidden="true" />
      </RouterLink>

      <div class="info">
        <RouterLink :to="{ name: 'product', params: { id: p.id } }" class="name">{{ p.name }}</RouterLink>
        <span class="muted cat">{{ p.category?.name }}</span>
        <strong class="price">{{ money(p.price) }} ₽</strong>
      </div>

      <div class="tools">
        <button class="btn btn-ghost" @click="openEdit(p)">Изменить</button>
        <button class="btn btn-danger" @click="remove(p)">Удалить</button>
      </div>
    </article>
  </div>

  <Teleport to="body">
    <div v-if="formOpen" class="backdrop" @click.self="formOpen = false">
      <div class="card modal" role="dialog" aria-modal="true">
        <h2>{{ editingId ? 'Изменить товар' : 'Новый товар' }}</h2>

        <form @submit.prevent="submit">
          <div class="field">
            <label for="name">Название</label>
            <input id="name" v-model="form.name" class="input" required minlength="5" maxlength="100" />
            <span class="hint">От 5 до 100 символов</span>
          </div>

          <div class="row">
            <div class="field">
              <label for="price">Цена, ₽</label>
              <input id="price" v-model="form.price" type="number" step="0.01" min="0.01" class="input" required />
            </div>

            <div class="field">
              <label for="category">Категория</label>
              <select id="category" v-model="form.category_id" class="input" required>
                <option value="" disabled>Выберите</option>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
          </div>

          <div class="field">
            <label for="description">Описание</label>
            <textarea id="description" v-model="form.description" class="input" rows="3" />
          </div>

          <div class="field">
            <label for="image">Ссылка на картинку</label>
            <input id="image" v-model="form.image_url" class="input" placeholder="https://…" />
          </div>

          <p v-if="formError" class="alert">{{ formError }}</p>

          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="formOpen = false">Отмена</button>
            <button class="btn" :disabled="busy">{{ busy ? 'Сохраняем…' : 'Сохранить' }}</button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 26px;
}

h1 {
  font-size: 26px;
  margin: 0 0 4px;
}

.sub {
  margin: 0;
  font-size: 14px;
}

.grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.block {
  height: 104px;
}

.empty {
  padding: 56px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.item {
  display: grid;
  grid-template-columns: 84px minmax(0, 1fr) auto;
  gap: 18px;
  align-items: center;
  padding: 14px 18px;
}

@media (max-width: 640px) {
  .item {
    grid-template-columns: 64px minmax(0, 1fr);
  }

  .tools {
    grid-column: 1 / -1;
  }
}

.thumb {
  width: 84px;
  height: 84px;
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

.info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.name {
  font-weight: 570;
}

.name:hover {
  color: var(--accent);
}

.cat {
  font-size: 13px;
}

.price {
  font-size: 16px;
  margin-top: 2px;
}

.tools {
  display: flex;
  gap: 8px;
}

.backdrop {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: rgba(8, 10, 15, 0.55);
  backdrop-filter: blur(3px);
  display: grid;
  place-items: center;
  padding: 20px;
  overflow-y: auto;
}

.modal {
  width: 100%;
  max-width: 520px;
  padding: 28px;
  box-shadow: var(--shadow-lg);
}

h2 {
  font-size: 20px;
  margin: 0 0 20px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

textarea.input {
  resize: vertical;
  font-family: inherit;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 6px;
}
</style>
