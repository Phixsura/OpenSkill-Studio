"use client";

interface Migration { oldEndpoint: string; newEndpoint: string; deadline: string; status: string; }
interface Props { migrations: Migration[]; completedCount: number; totalCount: number; progressPct: number; consumerId: string; appName: string; }

const statusColors: Record<string, string> = {
  pending: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  in_progress: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  completed: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  overdue: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKConsumerEndpointMigrationTrackerCard({ migrations, completedCount, totalCount, progressPct, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Migration Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`text-sm font-bold ${progressPct >= 100 ? "text-green-600" : "text-blue-600"}`}>{completedCount}/{totalCount}</span>
      </div>
      <div className="mb-3 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${progressPct >= 100 ? "bg-green-500" : "bg-blue-500"}`} style={{ width: `${progressPct}%` }} />
      </div>
      {migrations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No migrations</p>
      ) : (
        <div className="space-y-1">
          {migrations.map((m) => (
            <div key={m.oldEndpoint} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div className="flex items-center gap-1">
                <code className="text-gray-500 line-through">{m.oldEndpoint}</code>
                <span className="text-gray-400">→</span>
                <code className="text-blue-600 dark:text-blue-400">{m.newEndpoint}</code>
              </div>
              <span className={`rounded px-1 py-0.5 text-[9px] ${statusColors[m.status] ?? ""}`}>{m.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
