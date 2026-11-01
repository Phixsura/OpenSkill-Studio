"use client";
interface TenantRl { tenantId: string; allowed: number; denied: number; denyRate: number; }
interface RlAnalyticsPanelProps { tenants: TenantRl[]; totalAllowed: number; totalDenied: number; overallDenyRate: number; }
export function RlAnalyticsPanel({ tenants, totalAllowed, totalDenied, overallDenyRate }: RlAnalyticsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚫 Rate Limit Analytics</h3>
        <span className="text-xs text-gray-400">{totalAllowed.toLocaleString()} allowed · {totalDenied.toLocaleString()} denied ({overallDenyRate}%)</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tenants.map(t => (
          <div key={t.tenantId} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{t.tenantId}</span>
            <span className={t.denyRate > 50 ? "text-red-500" : "text-gray-400"}>
              {t.denied} denied ({t.denyRate}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
