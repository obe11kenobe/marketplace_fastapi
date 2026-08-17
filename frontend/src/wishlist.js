import { reactive, computed } from 'vue'
import { api, getToken } from './api'

const state = reactive({
  ids: new Set(),
  items: [],
  error: '',
})

function fill(items) {
  state.items = items
  state.ids = new Set(items.map((f) => f.product_id))
}

async function load() {
  if (!getToken()) return
  try {
    state.error = ''
    fill(await api.wishlist())
  } catch (e) {
    state.error = e.message
  }
}

export function useWishlist() {
  return {
    items: computed(() => state.items),
    count: computed(() => state.items.length),
    error: computed(() => state.error),

    has: (id) => state.ids.has(id),

    // Возвращает true, если товар добавлен, false — если убран.
    async toggle(productId) {
      if (state.ids.has(productId)) {
        await api.removeFromWishlist(productId)
        fill(state.items.filter((f) => f.product_id !== productId))
        return false
      }
      const favorite = await api.addToWishlist(productId)
      fill([favorite, ...state.items])
      return true
    },

    load,

    reset() {
      fill([])
    },
  }
}
