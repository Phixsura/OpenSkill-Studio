"use client";

interface Task { task_id: string; name: string; cron: string; status: string; last_run: string; success_count: number; fail_count: number; }
interface ScheduledTaskManagerProps { tasks: Task[]; onToggle: (id: string) => void; onDelete: (id: string) => void; }

export function ScheduledTaskManager({ tasks, onToggle, onDelete }: ScheduledTaskManagerProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Scheduled Tasks</h2>
      {tasks.map(t => (
        <div key={t.task_id} className="rounded-lg border p-3 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{t.name}</p>
              <p className="font-mono text-xs text-gray-400">{t.cron}</p>
            </div>
            <span className={`rounded-full px-2 py-0.5 text-xs ${t.status === "active" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>
              {t.status}
            </span>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
            <span>✅ {t.success_count} · ❌ {t.fail_count}</span>
            <div className="flex gap-2">
              <button onClick={() => onToggle(t.task_id)} className="text-blue-500">{t.status === "active" ? "Pause" : "Resume"}</button>
              <button onClick={() => onDelete(t.task_id)} className="text-red-500">Delete</button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
