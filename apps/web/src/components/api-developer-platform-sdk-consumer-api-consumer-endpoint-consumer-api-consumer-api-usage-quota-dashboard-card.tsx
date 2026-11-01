"use client";

interface Quota { name: string; used: number; limit: number; category: string; }
interface Props { quotas: Quota[]; overallPct: number; atRisk: number; exceeded: number; consumerId: string; appName: string; }

const catIcons: Record<string, string> = { requests: "📊", resources: "🔧", storage: "💾", compute: "⚡", bandwidth: "🌐" };

export default function APIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiUsageQuotaDashboardCard({ quotas, overallPct, atRisk, exceeded, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Quota Dashboard</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <div className="text-right">
          <div className={`text-lg font-bold ${overallPct >= 80 ? "text-red-600" : overallPct >= 60 ? "text-amber-600" : "text-green-600"}`}>{overallPct}%</div>
          {(atRisk > 0 || exceeded > 0) && <div className="text-[9px] text-gray-400">{exceeded > 0 ? `${exceeded} exceeded` : ""}{atRisk > 0 ? ` ${atRisk} at risk` : ""}</div>}
        </div>
      </div>
      {quotas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quotas</p>
      ) : (
        <div className="space-y-2">
          {quotas.map((q) => {
            const pct = q.limit > 0 ? Math.round((q.used / q.limit) * 100) : 0;
            return (
              <div key={q.name}>
                <div className="flex justify-between text-[11px]">
                  <span className="text-gray-700 dark:text-gray-300">{catIcons[q.category] ?? ""} {q.name}</span>
                  <span className="text-gray-400">{q.used.toLocaleString()}/{q.limit.toLocaleString()}</span>
                </div>
                <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div className={`h-full rounded-full ${pct >= 100 ? "bg-red-500" : pct >= 80 ? "bg-amber-500" : "bg-blue-500"}`} style={{ width: `${Math.min(pct, 100)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
