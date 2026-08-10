let onUnauthorized = () => {}

export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn
}

export function getToken() {
  return localStorage.getItem('token') || ''
}

export function setToken(token) {
  if (token) localStorage.setItem('token', token)
  else localStorage.removeItem('token')
}

async function request(url, { method = 'GET', body, auth = false } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(url, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  if (res.status === 401 && auth) {
    setToken('')
    onUnauthorized()
  }

  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || `Ошибка ${res.status}`)
  }

  return res.status === 204 ? null : res.json()
}

export const api = {
  categories: () => request('/api/categories'),
  products: () => request('/api/products'),
  product: (id) => request(`/api/products/${id}`),
  productsByCategory: (id) => request(`/api/products/category/${id}`),
  cart: (items) => request('/api/cart', { method: 'POST', body: items }),

  register: (email, password) =>
    request('/api/auth/register', { method: 'POST', body: { email, password } }),
  login: (email, password) =>
    request('/api/auth/login', { method: 'POST', body: { email, password } }),
  me: () => request('/api/auth/me', { auth: true }),

  createOrder: (cart) => request('/api/orders', { method: 'POST', body: { cart }, auth: true }),
  orders: () => request('/api/orders', { auth: true }),
  order: (id) => request(`/api/orders/${id}`, { auth: true }),
}
