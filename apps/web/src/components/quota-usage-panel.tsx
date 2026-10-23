"use client";

interface QuotaItem { resource: string; current: number; limit: number; unlimited: boolean; }
interface QuotaUsagePanelProps { plan: string; quotas: QuotaItem[]; onUpgrade: () => void; }

export function QuotaUsagePanel({ plan, quotas, onUpgrade }: QuotaUsagePanelProps) {
  const anyNearLimit = quotas.some(q => !q.unlimited && q.current / Math.max(q.limit, 1) > 0.8);
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold">Resource Quotas</h3>
          <p className="text-xs text-gray-400">Plan: {plan}</p>
        </div>
        {anyNearLimit && <button onClick={onUpgrade} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">Upgrade</button>}
      </div>
      <ul className="mt-3 space-y-2">
        {quotas.map(q => {
          const pct = q.unlimited ? 0 : Math.round((q.current / Math.max(q.limit, 1)) * 100);
          return (
            <li key={q.resource}>
              <div className="flex justify-between text-xs">
                <span className="font-medium capitalize">{q.resource.replace(/_/g, " ")}</span>
                <span className="text-gray-400">{q.unlimited ? `${q.current} / ∞` : `${q.current} / ${q.limit}`}</span>
              </div>
              {!q.unlimited && (
                <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div className={`h-full rounded-full ${pct > 90 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                    style={{ width: `${pct}%` }} />
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
