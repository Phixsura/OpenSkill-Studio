"use client";

interface TaskInfo { task_id: string; consumer_id: string; from_version: string; to_version: string; status: string; }
interface Props { tasks: TaskInfo[]; progress: Record<string, number>; appName: string; }

const sDot: Record<string, string> = { pending: "bg-gray-400", in_progress: "bg-blue-500", completed: "bg-green-500", failed: "bg-red-500" };

export default function APIDeveloperAPIApiMigrationTrackerCard({ tasks, progress, appName }: Props) {
  const total = Object.values(progress).reduce((s, v) => s + v, 0);
  const completedPct = total > 0 ? Math.round((progress.completed ?? 0) / total * 100) : 0;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚚 Migration Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-blue-600">{completedPct}%</span>
      </div>
      <div className="mb-3 flex gap-2 text-[10px]">
        {Object.entries(progress).map(([s, c]) => c > 0 && <span key={s} className="text-gray-400">{s}: {c}</span>)}
      </div>
      {tasks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No migrations</p>
      ) : (
        <div className="space-y-1">
          {tasks.map((t) => (
            <div key={t.task_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${sDot[t.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{t.consumer_id}</span>
              </div>
              <span className="text-gray-400">{t.from_version} → {t.to_version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
