const FILTERS = ['All', 'Active', 'Completed']

export default function SearchFilter({ searchTerm, onSearchChange, filter, onFilterChange }) {
  return (
    <div className="flex flex-col gap-2">
      <input
        type="search"
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
        placeholder="Search todos…"
        aria-label="Search todos"
        className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm
                   placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <div className="flex gap-1" role="group" aria-label="Filter todos">
        {FILTERS.map((label) => (
          <button
            key={label}
            onClick={() => onFilterChange(label)}
            aria-pressed={filter === label}
            className={`flex-1 rounded-md px-3 py-1.5 text-xs font-medium transition-colors
              ${filter === label
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-300 text-gray-600 hover:bg-gray-50'}`}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  )
}
