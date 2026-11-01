"use client";
interface TenantThrottle { tenantId: string; allowed: number; throttled: number; throttleRate: number; }
interface ThrottleDashPanelProps { tenants: TenantThrottle[]; totalAllowed: number;
  totalThrottled: number; overallRate: number; }
export function ThrottleDashPanel({ tenants, totalAllowed, totalThrottled, overallRate }: ThrottleDashPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚦 Throttle Dashboard</h3>
        <span className="text-xs text-gray-400">
          {totalAllowed.toLocaleString()} allowed · {totalThrottled.toLocaleString()} throttled ({overallRate}%)
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tenants.map(t => (
          <div key={t.tenantId} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{t.tenantId}</span>
            <span className={t.throttleRate > 50 ? "text-red-500" : "text-gray-400"}>
              {t.throttled} throttled ({t.throttleRate}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
