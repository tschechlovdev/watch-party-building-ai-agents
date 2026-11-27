import { useState, useRef, useEffect } from 'react'

export default function TodoItem({ todo, onUpdate, onDelete }) {
  const [isEditing, setIsEditing] = useState(false)
  const [draft, setDraft] = useState(todo.title)
  const inputRef = useRef(null)

  useEffect(() => {
    if (isEditing) inputRef.current?.focus()
  }, [isEditing])

  function startEdit() {
    setDraft(todo.title)
    setIsEditing(true)
  }

  function cancelEdit() {
    setDraft(todo.title)
    setIsEditing(false)
  }

  function saveEdit() {
    const trimmed = draft.trim()
    if (!trimmed) { cancelEdit(); return }
    if (trimmed !== todo.title) onUpdate(todo.id, { title: trimmed })
    setIsEditing(false)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') saveEdit()
    if (e.key === 'Escape') cancelEdit()
  }

  return (
    <li className="flex items-center gap-3 rounded-lg bg-white px-4 py-3
                   border border-gray-200 shadow-sm">
      {/* Completion checkbox */}
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onUpdate(todo.id, { completed: !todo.completed })}
        className="h-4 w-4 rounded border-gray-300 accent-blue-600 cursor-pointer flex-shrink-0"
      />

      {/* Title — view or edit */}
      {isEditing ? (
        <input
          ref={inputRef}
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={saveEdit}
          onKeyDown={handleKeyDown}
          className="flex-1 rounded border border-blue-400 px-2 py-0.5 text-sm
                     focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      ) : (
        <span
          onClick={startEdit}
          title="Click to edit"
          className={`flex-1 text-sm cursor-pointer select-none
                      ${todo.completed ? 'line-through text-gray-400' : 'text-gray-800'}`}
        >
          {todo.title}
        </span>
      )}

      {/* Delete button */}
      <button
        onClick={() => onDelete(todo.id)}
        aria-label="Delete todo"
        className="ml-auto text-gray-400 hover:text-red-500 transition-colors text-lg
                   leading-none flex-shrink-0"
      >
        ×
      </button>
    </li>
  )
}
