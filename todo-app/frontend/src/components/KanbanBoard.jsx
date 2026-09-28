const COLUMNS = [
  { key: 'todo',        label: 'To Do' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'done',        label: 'Done' },
]

function KanbanCard({ todo, onStatusChange, onDelete }) {
  const otherColumns = COLUMNS.filter((c) => c.key !== todo.status)

  return (
    <div className={`rounded-lg border bg-white px-3 py-2 shadow-sm text-sm
                     ${todo.status === 'done' ? 'opacity-60' : ''}`}>
      <p className={`mb-2 ${todo.status === 'done' ? 'line-through text-gray-400' : 'text-gray-800'}`}>
        {todo.title}
      </p>
      <div className="flex flex-wrap gap-1 items-center justify-between">
        <div className="flex flex-wrap gap-1">
          {otherColumns.map((col) => (
            <button
              key={col.key}
              onClick={() => onStatusChange(todo.id, col.key)}
              className="text-xs px-2 py-0.5 rounded border border-gray-200
                         text-gray-500 hover:text-blue-600 hover:border-blue-300
                         transition-colors"
            >
              → {col.label}
            </button>
          ))}
        </div>
        <button
          onClick={() => onDelete(todo.id)}
          aria-label="Delete todo"
          className="text-gray-400 hover:text-red-500 transition-colors text-base leading-none"
        >
          ×
        </button>
      </div>
    </div>
  )
}

export default function KanbanBoard({ todos, onStatusChange, onDelete }) {
  return (
    <div className="flex gap-3 items-start overflow-x-auto pb-2">
      {COLUMNS.map((col) => {
        const cards = todos.filter((t) => t.status === col.key)
        return (
          <div key={col.key} className="flex-1 min-w-48">
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                {col.label}
              </h2>
              <span className="text-xs text-gray-400 bg-gray-100 rounded-full px-2 py-0.5">
                {cards.length}
              </span>
            </div>
            <div className="flex flex-col gap-2">
              {cards.length === 0 ? (
                <p className="text-xs text-gray-300 text-center py-4">Empty</p>
              ) : (
                cards.map((todo) => (
                  <KanbanCard
                    key={todo.id}
                    todo={todo}
                    onStatusChange={onStatusChange}
                    onDelete={onDelete}
                  />
                ))
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
