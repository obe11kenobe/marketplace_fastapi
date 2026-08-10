import { reactive, readonly } from 'vue'

const state = reactive({ items: [] })
let nextId = 1

export const toasts = readonly(state)

export function notify(message, type = 'success') {
  const id = nextId++
  state.items.push({ id, message, type })
  setTimeout(() => {
    const i = state.items.findIndex((t) => t.id === id)
    if (i !== -1) state.items.splice(i, 1)
  }, 3500)
}
