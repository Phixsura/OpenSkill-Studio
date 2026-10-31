"use client";
interface LimitCheck { resource: string; current: number; limit: number; pct: number; exceeded: boolean; warning: boolean; }
interface TenantLimitPanelProps { tenantId: string; checks: LimitCheck[]; exceeded: number; warnings: number; }
export function TenantLimitPanel({ tenantId, checks, exceeded, warnings }: TenantLimitPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Tenant Limits: {tenantId}</h3>
        <span className={`text-xs ${exceeded > 0 ? "text-red-500" : warnings > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {exceeded > 0 ? `❌ ${exceeded} exceeded` : warnings > 0 ? `⚠ ${warnings} warning` : "✅ OK"}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {checks.map(c => (
          <div key={c.resource} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-0.5">
              <span className={c.exceeded ? "text-red-600 font-bold" : ""}>{c.resource}</span>
              <span className="text-gray-400">{c.current}/{c.limit} ({c.pct}%)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${c.exceeded ? "bg-red-500" : c.warning ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(c.pct, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
