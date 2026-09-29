const COLUMNS = [
  { key: 'todo', label: 'To Do' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'done', label: 'Done' },
]

const OTHER_COLUMNS = {
  todo: [
    { value: 'in_progress', label: 'Move to In Progress' },
    { value: 'done', label: 'Move to Done' },
  ],
  in_progress: [
    { value: 'todo', label: 'Move to To Do' },
    { value: 'done', label: 'Move to Done' },
  ],
  done: [
    { value: 'todo', label: 'Move back to To Do' },
  ],
}

export default function KanbanBoard({ todos, onStatusChange }) {
  return (
    <div className="flex gap-4 overflow-x-auto pb-2">
      {COLUMNS.map(({ key, label }) => {
        const cards = todos.filter((t) => t.status === key)
        return (
          <div
            key={key}
            className="flex-1 min-w-[200px] bg-gray-100 rounded-xl p-3"
          >
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold text-gray-700 text-sm">{label}</h2>
              <span className="text-xs font-medium bg-gray-200 text-gray-500 rounded-full px-2 py-0.5">
                {cards.length}
              </span>
            </div>

            <div className="flex flex-col gap-2">
              {cards.map((todo) => (
                <div
                  key={todo.id}
                  className="bg-white rounded-lg shadow-sm px-3 py-2"
                >
                  <p
                    className={`text-sm text-gray-800 mb-2 ${
                      key === 'done' ? 'line-through text-gray-400' : ''
                    }`}
                  >
                    {todo.title}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {OTHER_COLUMNS[key].map(({ value, label: btnLabel }) => (
                      <button
                        key={value}
                        onClick={() => onStatusChange(todo.id, value)}
                        className="text-xs bg-gray-100 hover:bg-blue-100 hover:text-blue-700
                                   text-gray-600 rounded px-2 py-0.5 transition-colors"
                      >
                        {btnLabel}
                      </button>
                    ))}
                  </div>
                </div>
              ))}

              {cards.length === 0 && (
                <p className="text-xs text-gray-400 text-center py-4">No items</p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
