"use client";

interface SyncJob { source: string; destination: string; totalRecords: number;
  synced: number; failed: number; status: string; }
interface DataSyncStatusProps { jobs: SyncJob[]; totalSynced: number;
  totalFailed: number; successRate: number; }

export function DataSyncStatus({ jobs, totalSynced, totalFailed, successRate }: DataSyncStatusProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Data Sync</h3>
        <span className="text-xs text-gray-400">{jobs.length} jobs · {successRate}% success</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {jobs.map((j, i) => {
          const pct = Math.round(((j.synced + j.failed) / Math.max(j.totalRecords, 1)) * 100);
          return (
            <div key={i} className="px-4 py-2.5">
              <div className="flex justify-between text-xs mb-1">
                <span className="font-mono">{j.source} → {j.destination}</span>
                <span className="text-gray-400">{j.synced}/{j.totalRecords} · {j.status}</span>
              </div>
              <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${j.failed > 0 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
