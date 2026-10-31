"use client";

interface ScheduledTaskInfo {
  task_id: string;
  name: string;
  schedule: string;
  status: "enabled" | "disabled" | "running";
  run_count: number;
  last_run_at: string | null;
  next_run_at: string | null;
  last_error: string | null;
}

interface CronSchedulerCardProps {
  tasks: ScheduledTaskInfo[];
  appName: string;
}

const STATUS_ICONS: Record<string, { icon: string; color: string }> = {
  enabled: { icon: "✓", color: "text-green-600 dark:text-green-400" },
  disabled: { icon: "⏸", color: "text-gray-400" },
  running: { icon: "▶", color: "text-blue-600 dark:text-blue-400" },
};

function timeAgo(iso: string | null): string {
  if (!iso) return "never";
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

function timeUntil(iso: string | null): string {
  if (!iso) return "—";
  const diff = new Date(iso).getTime() - Date.now();
  if (diff <= 0) return "overdue";
  if (diff < 60_000) return `${Math.ceil(diff / 1000)}s`;
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m`;
  return `${Math.floor(diff / 3_600_000)}h`;
}

export default function CronSchedulerCard({ tasks, appName }: CronSchedulerCardProps) {
  const enabledCount = tasks.filter((t) => t.status === "enabled" || t.status === "running").length;
  const errorCount = tasks.filter((t) => t.last_error).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Scheduled Tasks
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{enabledCount} active</span>
          {errorCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {errorCount} errors
            </span>
          )}
        </div>
      </div>

      {tasks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No scheduled tasks</p>
      ) : (
        <div className="space-y-2">
          {tasks.map((t) => {
            const st = STATUS_ICONS[t.status] ?? STATUS_ICONS.disabled;
            return (
              <div
                key={t.task_id}
                className="rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`text-sm ${st.color}`}>{st.icon}</span>
                    <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                      {t.name}
                    </span>
                    <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-500 dark:bg-gray-800">
                      {t.schedule}
                    </span>
                  </div>
                  <span className="text-[11px] text-gray-400">{t.run_count} runs</span>
                </div>
                <div className="mt-1 flex items-center gap-3 text-[11px] text-gray-400">
                  <span>Last: {timeAgo(t.last_run_at)}</span>
                  {t.status === "enabled" && <span>Next: {timeUntil(t.next_run_at)}</span>}
                  {t.last_error && <span className="text-red-500">{t.last_error}</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
