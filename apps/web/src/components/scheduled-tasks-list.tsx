"use client";

interface Task { name: string; cron: string; description: string; }
interface ScheduledTasksListProps { tasks: Task[]; onPause: (name: string) => void; }

export function ScheduledTasksList({ tasks, onPause }: ScheduledTasksListProps) {
  if (tasks.length === 0) return <p className="text-sm text-gray-400">No scheduled tasks.</p>;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Scheduled Tasks</h3>
      <ul className="mt-3 space-y-2">
        {tasks.map(t => (
          <li key={t.name} className="flex items-center justify-between rounded border p-2 dark:border-gray-700">
            <div>
              <p className="text-sm font-medium">{t.name}</p>
              <p className="text-xs text-gray-400">{t.description} · <code className="text-xs">{t.cron}</code></p>
            </div>
            <button onClick={() => onPause(t.name)} className="rounded border px-2 py-1 text-xs hover:bg-gray-50 dark:border-gray-600">
              ⏸ Pause
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
