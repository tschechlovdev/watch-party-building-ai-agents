export default function AnalyticsDashboard({ stats, loading, error }) {
  if (loading) {
    return <p className="text-center text-sm text-gray-400 py-8">Loading analytics…</p>
  }

  if (error) {
    return (
      <p className="text-center text-sm text-red-500 py-8">{error}</p>
    )
  }

  if (!stats) return null

  const {
    total,
    completed,
    active,
    completion_rate,
    created_last_7_days,
    completed_last_7_days,
  } = stats

  const metrics = [
    { label: 'Total Todos', value: total },
    { label: 'Completed', value: completed },
    { label: 'Active', value: active },
    { label: 'Created (last 7 days)', value: created_last_7_days },
    { label: 'Completed (last 7 days)', value: completed_last_7_days },
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {metrics.map(({ label, value }) => (
          <div key={label} className="rounded-lg bg-white border border-gray-200 px-4 py-3 shadow-sm">
            <p className="text-xs text-gray-500">{label}</p>
            <p className="mt-1 text-2xl font-semibold text-gray-800">{value}</p>
          </div>
        ))}
      </div>

      <div className="rounded-lg bg-white border border-gray-200 px-4 py-4 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-medium text-gray-700">Completion Rate</p>
          <p className="text-sm font-semibold text-gray-800">{completion_rate}%</p>
        </div>
        <div className="h-3 w-full rounded-full bg-gray-200 overflow-hidden">
          <div
            className="h-3 rounded-full bg-green-500 transition-all"
            style={{ width: `${completion_rate}%` }}
          />
        </div>
      </div>
    </div>
  )
}
