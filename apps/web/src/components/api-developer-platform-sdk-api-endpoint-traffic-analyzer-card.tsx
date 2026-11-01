"use client";

interface TrafficInfo { endpoint: string; method: string; total_requests: number; unique_consumers: number; traffic_tier: string; peak_rps: number; }
interface Props { traffic: TrafficInfo[]; tierCounts: Record<string, number>; appName: string; }

const mColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600" };
const tBadge: Record<string, string> = { mega: "bg-purple-100 text-purple-700", high: "bg-red-100 text-red-700", medium: "bg-yellow-100 text-yellow-700", low: "bg-gray-100 text-gray-600" };

export default function APIDeveloperPlatformSDKApiEndpointTrafficAnalyzerCard({ traffic, tierCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔥 Traffic Analyzer</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {traffic.length} endpoints</p>
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(tierCounts).map(([tier, count]) => (
          <span key={tier} className={`rounded px-1.5 py-0.5 text-[10px] ${tBadge[tier] ?? ""}`}>{tier}: {count}</span>
        ))}
      </div>
      {traffic.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No traffic data</p>
      ) : (
        <div className="space-y-1">
          {traffic.slice(0, 5).map((t) => (
            <div key={`${t.method}-${t.endpoint}`} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1">
                <span className={`font-mono font-bold ${mColor[t.method] ?? ""}`}>{t.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{t.endpoint}</span>
              </div>
              <span className="text-gray-400">{t.total_requests.toLocaleString()} · {t.peak_rps} rps</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
