async function request(url, options) {
  const res = await fetch(url, options)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Ошибка ${res.status}`)
  }
  return res.json()
}

export const api = {
  categories: () => request('/api/categories'),
  category: (id) => request(`/api/categories/${id}`),
  products: () => request('/api/products'),
  product: (id) => request(`/api/products/${id}`),
  productsByCategory: (id) => request(`/api/products/category/${id}`),
  cart: (items) =>
    request('/api/cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(items),
    }),
}
