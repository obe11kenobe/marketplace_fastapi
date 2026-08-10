import { reactive, readonly, computed } from 'vue'
import { api } from './api'

// ponytail: один общий reactive вместо Pinia — стор здесь ровно один.
// Ставить Pinia, когда сторов станет несколько или понадобится их девтулс.
const state = reactive({
  items: JSON.parse(localStorage.getItem('cart') || '{}'), // { product_id: quantity }
  details: { items: [], total: 0, items_count: 0 },
  error: '',
})

function persist() {
  localStorage.setItem('cart', JSON.stringify(state.items))
}

// Состав и суммы считает бэкенд — цены на клиенте не дублируются и не устаревают.
async function sync() {
  try {
    state.error = ''
    state.details = await api.cart(state.items)
  } catch (e) {
    state.error = e.message
  }
}

export function useCart() {
  return {
    items: readonly(state).items,
    details: computed(() => state.details),
    error: computed(() => state.error),
    count: computed(() => state.details.items_count),
    total: computed(() => state.details.total),

    quantityOf: (id) => state.items[id] || 0,

    add(id, quantity = 1) {
      state.items[id] = (state.items[id] || 0) + quantity
      persist()
      return sync()
    },

    setQuantity(id, quantity) {
      if (quantity > 0) state.items[id] = quantity
      else delete state.items[id]
      persist()
      return sync()
    },

    remove(id) {
      delete state.items[id]
      persist()
      return sync()
    },

    clear() {
      Object.keys(state.items).forEach((k) => delete state.items[k])
      persist()
      return sync()
    },

    sync,
  }
}
