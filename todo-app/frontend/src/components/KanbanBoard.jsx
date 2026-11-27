import { useState } from 'react'
import KanbanCard from './KanbanCard'

const COLUMNS = [
  { key: 'todo', label: 'To Do' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'done', label: 'Done' },
]

export default function KanbanBoard({ todos, onUpdate, onDelete }) {
  const [dragOverColumn, setDragOverColumn] = useState(null)

  function handleDrop(e, columnKey) {
    e.preventDefault()
    setDragOverColumn(null)
    const id = Number(e.dataTransfer.getData('text/plain'))
    const todo = todos.find((t) => t.id === id)
    if (todo && todo.status !== columnKey) onUpdate(id, { status: columnKey })
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {COLUMNS.map((col) => {
        const cards = todos.filter((t) => t.status === col.key)
        return (
          <div
            key={col.key}
            onDragOver={(e) => {
              e.preventDefault()
              setDragOverColumn(col.key)
            }}
            onDragLeave={() => setDragOverColumn(null)}
            onDrop={(e) => handleDrop(e, col.key)}
            className={`rounded-lg border border-gray-200 p-3 min-h-32
                        ${dragOverColumn === col.key ? 'ring-2 ring-blue-400 bg-blue-50' : 'bg-gray-100'}`}
          >
            <h2 className="mb-3 text-sm font-semibold text-gray-600">
              {col.label} ({cards.length})
            </h2>
            <div className="flex flex-col gap-2">
              {cards.map((todo) => (
                <KanbanCard key={todo.id} todo={todo} onDelete={onDelete} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
