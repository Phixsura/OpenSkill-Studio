"use client";

interface MigrationInfo { consumer_id: string; from_version: string; to_version: string; migrated: boolean; }
interface Props { migrations: MigrationInfo[]; progress: { total: number; migrated: number; pct: number }; appName: string; }

export default function APIDeveloperAPIMigrationStatusCard({ migrations, progress, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Migration Status</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{progress.pct}%</span>
      </div>
      <div className="mb-3 h-2 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className="h-2 rounded-full bg-green-500" style={{ width: `${progress.pct}%` }} />
      </div>
      <p className="mb-2 text-center text-[10px] text-gray-400">{progress.migrated}/{progress.total} migrated</p>
      {migrations.length > 0 && (
        <div className="space-y-0.5">
          {migrations.filter((m) => !m.migrated).slice(0, 5).map((m) => (
            <div key={m.consumer_id} className="flex items-center justify-between text-[10px]">
              <span className="text-gray-700 dark:text-gray-300">{m.consumer_id}</span>
              <span className="text-gray-400">{m.from_version} → {m.to_version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
