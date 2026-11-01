"use client";

interface StatsInfo { consumer_id: string; success_rate: number; health_status: string; total_deliveries: number; avg_latency_ms: number; retry_rate: number; }
interface Props { stats: StatsInfo[]; healthBreakdown: Record<string, number>; appName: string; }

const hColor: Record<string, string> = { excellent: "text-green-600", good: "text-blue-600", fair: "text-yellow-600", poor: "text-red-600" };

export default function APIDeveloperPlatformSDKApiDeveloperApiConsumerWebhookStatsCard({ stats, healthBreakdown, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Consumer Webhook Stats</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {stats.length} consumers</p>
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(healthBreakdown).map(([h, c]) => (
          <span key={h} className={`text-[10px] font-medium ${hColor[h] ?? ""}`}>{h}: {c}</span>
        ))}
      </div>
      {stats.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No webhook stats</p>
      ) : (
        <div className="space-y-1">
          {stats.slice(0, 5).map((s) => (
            <div key={s.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              <span className={hColor[s.health_status] ?? ""}>{s.success_rate}% · {s.health_status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
