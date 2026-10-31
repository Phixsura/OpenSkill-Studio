"use client";

interface StatsInfo { destination: string; count: number; avg_ms: number; p50_ms: number; p99_ms: number; }
interface Props { stats: StatsInfo[]; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiWebhookLatencyTrackerCard({ stats, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Webhook Latency</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {stats.length} destinations</p>
      </div>
      {stats.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No latency data</p>
      ) : (
        <div className="space-y-2">
          {stats.map((s) => (
            <div key={s.destination} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{new URL(s.destination).hostname}</span>
                <span className="text-gray-400">{s.count} deliveries</span>
              </div>
              <div className="mt-1 grid grid-cols-3 gap-1 text-center text-[10px]">
                <div><p className="font-bold text-green-600">{s.avg_ms}ms</p><p className="text-[8px] text-gray-400">avg</p></div>
                <div><p className="font-bold text-blue-600">{s.p50_ms}ms</p><p className="text-[8px] text-gray-400">p50</p></div>
                <div><p className="font-bold text-red-500">{s.p99_ms}ms</p><p className="text-[8px] text-gray-400">p99</p></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
