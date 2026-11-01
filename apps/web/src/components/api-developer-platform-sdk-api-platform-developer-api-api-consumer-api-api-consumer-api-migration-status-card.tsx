"use client";

interface MigrationInfo { consumer_id: string; from_version: string; to_version: string; state: string; progress_pct: number; }
interface Props { migrations: MigrationInfo[]; inProgressCount: number; appName: string; }

const stateColor: Record<string, string> = { not_started: "text-gray-400", in_progress: "text-blue-600 dark:text-blue-400", testing: "text-yellow-600 dark:text-yellow-400", completed: "text-green-600 dark:text-green-400", rolled_back: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiMigrationStatusCard({ migrations, inProgressCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Migration Status</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {inProgressCount > 0 && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{inProgressCount} migrating</span>}
      </div>
      {migrations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No migrations</p>
      ) : (
        <div className="space-y-1.5">
          {migrations.map((m) => (
            <div key={m.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{m.consumer_id}: {m.from_version} → {m.to_version}</span>
                <span className={stateColor[m.state]}>{m.state.replace("_", " ")}</span>
              </div>
              {m.state === "in_progress" && <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800"><div className="h-1 rounded-full bg-blue-500" style={{ width: `${m.progress_pct}%` }} /></div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
