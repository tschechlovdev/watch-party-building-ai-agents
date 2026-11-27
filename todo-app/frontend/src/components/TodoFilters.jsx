import { DUE_FILTERS } from '../dueDate'

const STATUS_OPTIONS = [
  { key: 'all', label: 'All' },
  { key: 'active', label: 'Active' },
  { key: 'completed', label: 'Completed' },
]

const PRIORITY_OPTIONS = [
  { key: 'all', label: 'All priorities' },
  { key: 'high', label: 'High' },
  { key: 'medium', label: 'Medium' },
  { key: 'low', label: 'Low' },
]

const DUE_OPTIONS = DUE_FILTERS.map((f) =>
  f.key === 'all' ? { ...f, label: 'All dates' } : f,
)

const selectClass =
  'rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-700 ' +
  'focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer'

export default function TodoFilters({
  search,
  onSearchChange,
  filter,
  onFilterChange,
  priorityFilter,
  onPriorityChange,
  dueFilter,
  onDueChange,
}) {
  return (
    <div
      role="group"
      aria-label="Filter todos"
      className="mb-4 flex flex-wrap items-center gap-2"
    >
      <input
        type="text"
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
        placeholder="Search…"
        aria-label="Search todos"
        className="min-w-0 flex-1 rounded-lg border border-gray-300 px-3 py-1.5 text-sm
                   focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <select
        value={filter}
        onChange={(e) => onFilterChange(e.target.value)}
        aria-label="Filter by status"
        className={selectClass}
      >
        {STATUS_OPTIONS.map((o) => (
          <option key={o.key} value={o.key}>
            {o.label}
          </option>
        ))}
      </select>

      <select
        value={priorityFilter}
        onChange={(e) => onPriorityChange(e.target.value)}
        aria-label="Filter by priority"
        className={selectClass}
      >
        {PRIORITY_OPTIONS.map((o) => (
          <option key={o.key} value={o.key}>
            {o.label}
          </option>
        ))}
      </select>

      <select
        value={dueFilter}
        onChange={(e) => onDueChange(e.target.value)}
        aria-label="Filter by due date"
        className={selectClass}
      >
        {DUE_OPTIONS.map((o) => (
          <option key={o.key} value={o.key}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  )
}
