"use client";

interface StatsInfo { destination: string; total_delivered: number; total_failed: number; success_rate: number; avg_latency_ms: number; }
interface Props { stats: StatsInfo[]; appName: string; }

export default function APIDeveloperAPIWebhookDestinationStatsCard({ stats, appName }: Props) {
  const failing = stats.filter((s) => s.success_rate < 90).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Destination Stats</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{stats.length} destinations</span>
          {failing > 0 && <p className="text-[10px] text-red-500">{failing} failing</p>}
        </div>
      </div>
      {stats.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No destination stats</p>
      ) : (
        <div className="space-y-1">
          {stats.map((s) => (
            <div key={s.destination} className="flex items-center justify-between text-[11px]">
              <span className="truncate max-w-[150px] text-gray-700 dark:text-gray-300">{s.destination}</span>
              <span className={`text-gray-400 ${s.success_rate < 90 ? "text-red-500" : ""}`}>{s.success_rate}% · {s.avg_latency_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
