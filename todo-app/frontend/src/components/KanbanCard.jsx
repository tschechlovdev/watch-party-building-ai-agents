export default function KanbanCard({ todo, onDelete }) {
  function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', String(todo.id))
    e.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div
      draggable
      onDragStart={handleDragStart}
      className="flex items-center gap-2 rounded-lg bg-white px-3 py-2
                 border border-gray-200 shadow-sm cursor-grab"
    >
      <span
        className={`flex-1 text-sm select-none break-words min-w-0
                    ${todo.status === 'done' ? 'line-through text-gray-400' : 'text-gray-800'}`}
      >
        {todo.title}
      </span>
      <button
        onClick={() => onDelete(todo.id)}
        aria-label="Delete todo"
        className="text-gray-400 hover:text-red-500 transition-colors text-lg
                   leading-none flex-shrink-0"
      >
        ×
      </button>
    </div>
  )
}
