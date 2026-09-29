import { useState, useEffect } from 'react'
import { getTodos, createTodo, updateTodo, deleteTodo } from './api'
import AddTodo from './components/AddTodo'
import TodoList from './components/TodoList'
import KanbanBoard from './components/KanbanBoard'

export default function App() {
  const [todos, setTodos] = useState([])
  const [error, setError] = useState(null)
  const [view, setView] = useState('list')

  useEffect(() => {
    getTodos()
      .then(setTodos)
      .catch(() => setError('Failed to load todos.'))
  }, [])

  async function handleAdd(title) {
    try {
      const created = await createTodo(title)
      setTodos((prev) => [created, ...prev])
    } catch {
      setError('Failed to add todo.')
    }
  }

  async function handleUpdate(id, fields) {
    try {
      const updated = await updateTodo(id, fields)
      setTodos((prev) => prev.map((t) => (t.id === id ? updated : t)))
    } catch {
      setError('Failed to update todo.')
    }
  }

  async function handleStatusChange(id, newStatus) {
    try {
      const updated = await updateTodo(id, { status: newStatus })
      setTodos((prev) => prev.map((t) => (t.id === id ? updated : t)))
    } catch {
      setError('Failed to move todo.')
    }
  }

  async function handleDelete(id) {
    try {
      await deleteTodo(id)
      setTodos((prev) => prev.filter((t) => t.id !== id))
    } catch {
      setError('Failed to delete todo.')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="mx-auto w-full max-w-4xl">

        <h1 className="text-2xl font-semibold text-gray-800 mb-4 text-center">
          My Todos
        </h1>

        {/* View toggle */}
        <div className="flex justify-center gap-2 mb-6">
          <button
            onClick={() => setView('list')}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              view === 'list'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            List
          </button>
          <button
            onClick={() => setView('board')}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              view === 'board'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Board
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-2
                          text-sm text-red-700 flex justify-between items-center">
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-2 text-red-400 hover:text-red-600"
              aria-label="Dismiss error"
            >
              ×
            </button>
          </div>
        )}

        {view === 'list' ? (
          <div className="mx-auto max-w-md">
            <div className="mb-4">
              <AddTodo onAdd={handleAdd} />
            </div>

            <TodoList
              todos={todos}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
            />

            {todos.length > 0 && (
              <p className="mt-4 text-center text-xs text-gray-400">
                {todos.filter((t) => t.completed).length} / {todos.length} completed
              </p>
            )}
          </div>
        ) : (
          <div>
            <div className="mb-4 max-w-md mx-auto">
              <AddTodo onAdd={handleAdd} />
            </div>
            <KanbanBoard
              todos={todos}
              onStatusChange={handleStatusChange}
            />
          </div>
        )}
      </div>
    </div>
  )
}
