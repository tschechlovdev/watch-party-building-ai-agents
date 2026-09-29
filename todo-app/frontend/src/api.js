const BASE = '/api/todos'

async function request(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (res.status === 204) return null
  const data = await res.json()
  if (!res.ok) throw new Error(data.error ?? 'Request failed')
  return data
}

export const getTodos = () => request(BASE)

export const createTodo = (title) =>
  request(BASE, { method: 'POST', body: JSON.stringify({ title }) })

export const updateTodo = (id, fields) =>
  request(`${BASE}/${id}`, { method: 'PUT', body: JSON.stringify(fields) })

export const deleteTodo = (id) =>
  request(`${BASE}/${id}`, { method: 'DELETE' })

export const getStats = () => request(`${BASE}/stats`)
