"use client";

interface QueueStats {
  pending: number;
  running: number;
  completed: number;
  failed: number;
}

interface TaskInfo {
  task_id: string;
  task_type: string;
  priority: number;
  status: "pending" | "running" | "completed" | "failed";
  attempts: number;
  max_retries: number;
}

interface TaskQueueCardProps {
  stats: QueueStats;
  recentTasks: TaskInfo[];
  appName: string;
}

const statusDot: Record<string, string> = {
  pending: "bg-gray-400",
  running: "bg-blue-500",
  completed: "bg-green-500",
  failed: "bg-red-500",
};

export default function TaskQueueCard({ stats, recentTasks, appName }: TaskQueueCardProps) {
  const total = stats.pending + stats.running + stats.completed + stats.failed;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📬 Task Queue</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{total} tasks</span>
      </div>

      <div className="mb-3 grid grid-cols-4 gap-2 text-center">
        {(["pending", "running", "completed", "failed"] as const).map((s) => (
          <div key={s} className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{stats[s]}</p>
            <p className="text-[9px] text-gray-500">{s}</p>
          </div>
        ))}
      </div>

      {recentTasks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tasks</p>
      ) : (
        <div className="space-y-1">
          {recentTasks.map((t) => (
            <div key={t.task_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${statusDot[t.status]}`} />
                <span className="text-gray-700 dark:text-gray-300">{t.task_type}</span>
              </div>
              <span className="text-gray-400">
                P{t.priority} · {t.attempts}/{t.max_retries}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
