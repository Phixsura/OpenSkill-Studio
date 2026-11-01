"use client";

interface Quota { resource: string; used: number; limit: number; usagePct: number; status: string; }
interface Props { quotas: Quota[]; overallStatus: string; atRiskCount: number; consumerId: string; appName: string; }

const statusColors: Record<string, string> = { ok: "text-green-500", warning: "text-amber-500", exceeded: "text-red-500" };
const barColors: Record<string, string> = { ok: "bg-blue-500", warning: "bg-amber-500", exceeded: "bg-red-500" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiQuotaUsageSummaryCard({ quotas, overallStatus, atRiskCount, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Quota Summary</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`font-bold text-sm ${statusColors[overallStatus] ?? ""}`}>{overallStatus === "ok" ? "✅" : overallStatus === "warning" ? "⚠️" : "🔴"} {atRiskCount > 0 ? `${atRiskCount} at risk` : "All OK"}</span>
      </div>
      {quotas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quotas</p>
      ) : (
        <div className="space-y-2">
          {quotas.map((q) => (
            <div key={q.resource}>
              <div className="flex justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{q.resource}</span>
                <span className={statusColors[q.status] ?? ""}>{q.used}/{q.limit} ({q.usagePct}%)</span>
              </div>
              <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className={`h-full rounded-full ${barColors[q.status] ?? "bg-blue-500"}`} style={{ width: `${Math.min(q.usagePct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
