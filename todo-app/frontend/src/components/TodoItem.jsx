import { useState, useRef, useEffect } from 'react'
import { PRIORITIES, PRIORITY_LABELS, PRIORITY_STYLES } from '../priority'
import { dueClasses, formatDue, getDueState, todayLocal } from '../dueDate'

export default function TodoItem({ todo, onUpdate, onDelete }) {
  const dueState = getDueState(todo, todayLocal())
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
    <li className={`flex items-center gap-3 rounded-lg bg-white px-4 py-3
                    border shadow-sm
                    ${dueState === 'overdue' ? 'border-red-300'
                      : dueState === 'today' ? 'border-amber-300'
                      : 'border-gray-200'}`}>
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

      {/* Priority indicator + editor */}
      <select
        aria-label="Priority"
        value={todo.priority}
        onChange={(e) => onUpdate(todo.id, { priority: e.target.value })}
        className={`rounded-full border px-2 py-0.5 text-xs font-medium flex-shrink-0
                    cursor-pointer ${PRIORITY_STYLES[todo.priority] ?? PRIORITY_STYLES.medium}`}
      >
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>{PRIORITY_LABELS[p]}</option>
        ))}
      </select>

      {/* Due date — display, edit, clear */}
      {todo.due_date && (
        <span className={`text-xs flex-shrink-0 ${dueClasses(dueState)}`}>
          {formatDue(todo.due_date)}
        </span>
      )}
      <input
        type="date"
        value={todo.due_date ?? ''}
        onChange={(e) => onUpdate(todo.id, { due_date: e.target.value || null })}
        aria-label="Edit due date"
        className="w-28 rounded border border-gray-200 px-1 py-0.5 text-xs text-gray-600
                   flex-shrink-0"
      />
      {todo.due_date && (
        <button
          onClick={() => onUpdate(todo.id, { due_date: null })}
          aria-label="Clear due date"
          className="text-gray-400 hover:text-red-500 transition-colors text-sm
                     leading-none flex-shrink-0"
        >
          ×
        </button>
      )}

      {/* Delete button */}
      <button
        onClick={() => onDelete(todo.id)}
        aria-label="Delete todo"
        className="text-gray-400 hover:text-red-500 transition-colors text-lg
                   leading-none flex-shrink-0"
      >
        ×
      </button>
    </li>
  )
}
