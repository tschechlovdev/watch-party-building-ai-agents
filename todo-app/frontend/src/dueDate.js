const pad = (n) => String(n).padStart(2, '0')

// Local calendar date as YYYY-MM-DD (avoids the UTC shift of toISOString()).
export function todayLocal() {
  const d = new Date()
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

// "2025-06-15" -> "Due Jun 15"
export function formatDue(dueDate) {
  const [y, m, d] = dueDate.split('-').map(Number)
  const label = new Date(y, m - 1, d).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  })
  return `Due ${label}`
}

// Completed todos are never highlighted.
export function getDueState(todo, today) {
  if (!todo.due_date || todo.completed) return null
  if (todo.due_date < today) return 'overdue'
  if (todo.due_date === today) return 'today'
  return null
}

export const DUE_FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'overdue', label: 'Overdue' },
  { key: 'today', label: 'Due today' },
  { key: 'none', label: 'No due date' },
]

export function matchesFilter(todo, filter, today) {
  if (filter === 'overdue') return getDueState(todo, today) === 'overdue'
  if (filter === 'today') return getDueState(todo, today) === 'today'
  if (filter === 'none') return todo.due_date == null
  return true
}

export function dueClasses(state) {
  if (state === 'overdue') return 'text-red-600 font-medium'
  if (state === 'today') return 'text-amber-600 font-medium'
  return 'text-gray-500'
}
