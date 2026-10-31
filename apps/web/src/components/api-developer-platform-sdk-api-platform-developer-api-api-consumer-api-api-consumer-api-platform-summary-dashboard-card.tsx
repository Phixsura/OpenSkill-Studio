"use client";

interface Metric { name: string; value: number; unit: string; trend: string; }
interface Props { totalConsumers: number; activeConsumers: number; totalKeys: number; requestsToday: number; avgLatencyMs: number; errorRatePct: number; uptimePct: number; healthScore: number; metrics: Metric[]; activeIncidents: number; appName: string; }

const trendIcons: Record<string, string> = { up: "📈", down: "📉", stable: "➡️" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiPlatformSummaryDashboardCard({ totalConsumers, activeConsumers, totalKeys, requestsToday, avgLatencyMs, errorRatePct, uptimePct, healthScore, metrics, activeIncidents, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏠 Platform Summary</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-lg font-bold ${healthScore >= 80 ? "text-green-600" : healthScore >= 50 ? "text-amber-600" : "text-red-600"}`}>{healthScore}%</span>
      </div>
      {activeIncidents > 0 && <div className="mb-3 rounded bg-red-50 p-1.5 text-center text-[11px] text-red-700 dark:bg-red-900/20 dark:text-red-400">🚨 {activeIncidents} active incidents</div>}
      <div className="mb-3 grid grid-cols-4 gap-2 text-center text-[10px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{activeConsumers}/{totalConsumers}</div><div className="text-gray-400">Consumers</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{totalKeys}</div><div className="text-gray-400">Keys</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{uptimePct}%</div><div className="text-gray-400">Uptime</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className={`font-bold ${errorRatePct > 1 ? "text-red-600" : "text-green-600"}`}>{errorRatePct}%</div><div className="text-gray-400">Errors</div></div>
      </div>
      <div className="grid grid-cols-2 gap-2 text-[10px] text-gray-500">
        <span>Requests: {requestsToday.toLocaleString()}</span>
        <span>Latency: {avgLatencyMs}ms</span>
      </div>
      {metrics.length > 0 && (
        <div className="mt-2 space-y-0.5">{metrics.map((m) => (
          <div key={m.name} className="flex justify-between text-[10px]"><span className="text-gray-500">{m.name}</span><span className="text-gray-700 dark:text-gray-300">{m.value.toLocaleString()} {m.unit} {trendIcons[m.trend] ?? ""}</span></div>
        ))}</div>
      )}
    </div>
  );
}
