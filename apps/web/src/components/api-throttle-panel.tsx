"use client";

interface TenantUsage { tenantId: string; used: number; limit: number; pctUsed: number; }
interface ApiThrottlePanelProps { tenants: TenantUsage[]; totalTenants: number; }

export function ApiThrottlePanel({ tenants, totalTenants }: ApiThrottlePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚦 API Throttle</h3>
        <span className="text-xs text-gray-400">{totalTenants} tenants</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tenants.map(t => (
          <div key={t.tenantId} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-1">
              <span className="font-mono">{t.tenantId}</span>
              <span className={`${t.pctUsed > 90 ? "text-red-500" : "text-gray-400"}`}>{t.used}/{t.limit} ({t.pctUsed}%)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${t.pctUsed > 90 ? "bg-red-500" : t.pctUsed > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(t.pctUsed, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
