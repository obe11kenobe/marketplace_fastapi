import { reactive, computed } from 'vue'
import { api, getToken, setToken } from './api'

const state = reactive({
  user: null,
  ready: false,
})

export function useAuth() {
  return {
    user: computed(() => state.user),
    ready: computed(() => state.ready),
    isAuthenticated: computed(() => Boolean(state.user)),

    async restore() {
      if (getToken()) {
        try {
          state.user = await api.me()
        } catch {
          state.user = null
        }
      }
      state.ready = true
    },

    async login(email, password) {
      const tokens = await api.login(email, password)
      setToken(tokens.access_token)
      state.user = await api.me()
    },

    async register(email, password) {
      await api.register(email, password)
      await this.login(email, password)
    },

    logout() {
      setToken('')
      state.user = null
    },
  }
}
