import TodoItem from './TodoItem'

export default function TodoList({ todos, totalCount, onUpdate, onDelete }) {
  if (todos.length === 0) {
    return (
      <p className="text-center text-sm text-gray-400 py-8">
        {totalCount > 0 ? 'No matching todos.' : 'No todos yet. Add one above!'}
      </p>
    )
  }

  return (
    <ul className="flex flex-col gap-2">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </ul>
  )
}
