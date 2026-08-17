import { reactive, computed } from 'vue'
import { api, getToken, setToken } from './api'
import { useWishlist } from './wishlist'

const state = reactive({
  user: null,
  ready: false,
})

export function useAuth() {
  return {
    user: computed(() => state.user),
    ready: computed(() => state.ready),
    isAuthenticated: computed(() => Boolean(state.user)),
    isSeller: computed(() => state.user?.role === 'seller'),
    isAdmin: computed(() => state.user?.role === 'admin'),

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
      await useWishlist().load()
    },

    async register(email, password) {
      await api.register(email, password)
      await this.login(email, password)
    },

    logout() {
      setToken('')
      state.user = null
      useWishlist().reset()
    },
  }
}
