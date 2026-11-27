import { useState } from 'react'
import { PRIORITIES, PRIORITY_LABELS } from '../priority'

export default function AddTodo({ onAdd }) {
  const [title, setTitle] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [priority, setPriority] = useState('medium')

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = title.trim()
    if (!trimmed) return
    onAdd(trimmed, dueDate || null, priority)
    setTitle('')
    setDueDate('')
    setPriority('medium')
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="What needs to be done?"
        className="flex-1 min-w-0 rounded-lg border border-gray-300 px-3 py-2 text-sm
                   focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <input
        type="date"
        value={dueDate}
        onChange={(e) => setDueDate(e.target.value)}
        aria-label="Due date"
        className="rounded-lg border border-gray-300 px-2 py-2 text-sm text-gray-700
                   focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <select
        aria-label="Priority"
        value={priority}
        onChange={(e) => setPriority(e.target.value)}
        className="rounded-lg border border-gray-300 bg-white px-2 py-2 text-sm
                   focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>{PRIORITY_LABELS[p]}</option>
        ))}
      </select>
      <button
        type="submit"
        disabled={!title.trim()}
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white
                   hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40
                   transition-colors"
      >
        Add
      </button>
    </form>
  )
}
