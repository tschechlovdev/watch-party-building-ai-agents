import { PRIORITY_LABELS, PRIORITY_STYLES } from '../priority'

export default function PriorityBadge({ priority }) {
  const level = PRIORITY_LABELS[priority] ? priority : 'medium'
  return (
    <span
      className={`rounded-full border px-2 py-0.5 text-xs font-medium flex-shrink-0
                  ${PRIORITY_STYLES[level]}`}
    >
      {PRIORITY_LABELS[level]}
    </span>
  )
}
