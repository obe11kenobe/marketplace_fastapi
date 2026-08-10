<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
import { useAuth } from '../auth'
import { notify } from '../toast'

const auth = useAuth()
const users = ref([])
const loading = ref(true)
const error = ref('')
const saving = ref(null)

const ROLES = [
  { value: 'user', label: 'Покупатель' },
  { value: 'seller', label: 'Продавец' },
  { value: 'admin', label: 'Админ' },
]

const formatDate = (iso) =>
  new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })

async function load() {
  loading.value = true
  error.value = ''
  try {
    users.value = await api.users()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function changeRole(user, role) {
  if (role === user.role) return
  saving.value = user.id
  try {
    const updated = await api.setUserRole(user.id, role)
    Object.assign(user, updated)
    notify(`${user.email}: теперь ${ROLES.find((r) => r.value === role).label.toLowerCase()}`)
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
      <h1>Пользователи</h1>
      <p class="muted sub">Роль выдаётся только отсюда</p>
    </div>
    <span v-if="users.length" class="badge">{{ users.length }}</span>
  </header>

  <p v-if="error" class="alert">{{ error }}</p>

  <div v-if="loading" class="list">
    <div v-for="n in 3" :key="n" class="card skeleton block" />
  </div>

  <div v-else class="card table">
    <div v-for="user in users" :key="user.id" class="row" :class="{ busy: saving === user.id }">
      <div class="who">
        <span class="avatar" aria-hidden="true">{{ user.email[0].toUpperCase() }}</span>
        <div class="meta">
          <span class="email">
            {{ user.email }}
            <span v-if="user.id === auth.user.value?.id" class="you">это вы</span>
          </span>
          <span class="muted since">с {{ formatDate(user.created_at) }}</span>
        </div>
      </div>

      <div class="roles" role="group" :aria-label="`Роль пользователя ${user.email}`">
        <button
          v-for="r in ROLES"
          :key="r.value"
          class="chip"
          :class="{ active: user.role === r.value }"
          :disabled="user.id === auth.user.value?.id || saving === user.id"
          :title="user.id === auth.user.value?.id ? 'Нельзя менять роль самому себе' : ''"
          @click="changeRole(user, r.value)"
        >
          {{ r.label }}
        </button>
      </div>
    </div>
  </div>
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

.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.block {
  height: 72px;
}

.table {
  padding: 4px 8px;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 14px 12px;
  border-bottom: 1px solid var(--border);
  transition: opacity 0.15s ease;
}

.row:last-child {
  border-bottom: 0;
}

.row.busy {
  opacity: 0.55;
}

@media (max-width: 620px) {
  .row {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}

.who {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent), #8b5cf6);
  color: #fff;
  font-weight: 700;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.meta {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.email {
  font-weight: 540;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.you {
  font-size: 11px;
  font-weight: 650;
  padding: 2px 7px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
}

.since {
  font-size: 12.5px;
}

.roles {
  display: inline-flex;
  gap: 6px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 4px;
}

.chip {
  padding: 6px 12px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  font-size: 13.5px;
  font-weight: 520;
  color: var(--text-soft);
  white-space: nowrap;
  transition: background 0.14s ease, color 0.14s ease;
}

.chip:hover:not(:disabled):not(.active) {
  background: var(--bg-elevated);
  color: var(--text);
}

.chip.active {
  background: var(--accent);
  color: #fff;
}

.chip:disabled {
  cursor: not-allowed;
}

.chip:disabled:not(.active) {
  opacity: 0.4;
}
</style>
