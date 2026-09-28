export default function ViewToggle({ view, onViewChange }) {
  return (
    <div className="flex gap-1 rounded-lg bg-gray-100 p-1 w-fit">
      {['list', 'board'].map((v) => (
        <button
          key={v}
          onClick={() => onViewChange(v)}
          className={`px-3 py-1 rounded-md text-sm font-medium transition-colors capitalize
            ${view === v
              ? 'bg-white text-gray-800 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
            }`}
        >
          {v === 'list' ? 'List' : 'Board'}
        </button>
      ))}
    </div>
  )
}
