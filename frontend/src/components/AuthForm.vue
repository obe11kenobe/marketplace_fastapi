<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../auth'
import { notify } from '../toast'

const props = defineProps({
  mode: { type: String, required: true },
})

const auth = useAuth()
const route = useRoute()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const busy = ref(false)

const isLogin = props.mode === 'login'

async function submit() {
  busy.value = true
  error.value = ''
  try {
    if (isLogin) await auth.login(email.value, password.value)
    else await auth.register(email.value, password.value)

    notify(isLogin ? 'С возвращением!' : 'Аккаунт создан')
    router.push(route.query.redirect || '/')
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="wrap">
    <div class="card panel">
      <h1>{{ isLogin ? 'Вход' : 'Регистрация' }}</h1>
      <p class="muted sub">
        {{ isLogin ? 'Войдите, чтобы оформлять заказы' : 'Нужен только email и пароль' }}
      </p>

      <form @submit.prevent="submit">
        <div class="field">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" class="input" required
                 autocomplete="email" placeholder="you@example.com" />
        </div>

        <div class="field">
          <label for="password">Пароль</label>
          <input id="password" v-model="password" type="password" class="input" required
                 :minlength="isLogin ? 1 : 8"
                 :autocomplete="isLogin ? 'current-password' : 'new-password'"
                 placeholder="••••••••" />
          <span v-if="!isLogin" class="hint">Минимум 8 символов</span>
        </div>

        <p v-if="error" class="alert">{{ error }}</p>

        <button class="btn btn-lg btn-block" :disabled="busy">
          {{ busy ? 'Секунду…' : isLogin ? 'Войти' : 'Создать аккаунт' }}
        </button>
      </form>

      <p class="switch muted">
        <template v-if="isLogin">
          Нет аккаунта? <RouterLink :to="{ name: 'register', query: route.query }" class="link">Зарегистрироваться</RouterLink>
        </template>
        <template v-else>
          Уже есть аккаунт? <RouterLink :to="{ name: 'login', query: route.query }" class="link">Войти</RouterLink>
        </template>
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap {
  display: grid;
  place-items: start center;
  padding-top: 24px;
}

.panel {
  width: 100%;
  max-width: 420px;
  padding: 32px;
  box-shadow: var(--shadow);
}

h1 {
  font-size: 25px;
  margin: 0 0 6px;
}

.sub {
  margin: 0 0 24px;
  font-size: 14px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.switch {
  margin: 22px 0 0;
  text-align: center;
  font-size: 14px;
}

.link {
  color: var(--accent);
  font-weight: 550;
}

.link:hover {
  text-decoration: underline;
}
</style>
