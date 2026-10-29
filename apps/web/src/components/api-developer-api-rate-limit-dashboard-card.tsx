"use client";

interface SnapshotInfo { endpoint: string; limit: number; remaining: number; usage_pct: number; consumer_id: string; }
interface Props { snapshots: SnapshotInfo[]; hotspotCount: number; appName: string; }

export default function APIDeveloperAPIRateLimitDashboardCard({ snapshots, hotspotCount, appName }: Props) {
  const barColor = (pct: number) => pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Rate Limit Dashboard</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {hotspotCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{hotspotCount} hotspots</span>}
      </div>
      {snapshots.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate limit data</p>
      ) : (
        <div className="space-y-2">
          {snapshots.map((s, i) => (
            <div key={i}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{s.endpoint}</span>
                <span className="text-gray-400">{s.remaining}/{s.limit} remaining</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${barColor(s.usage_pct)}`} style={{ width: `${Math.min(s.usage_pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
