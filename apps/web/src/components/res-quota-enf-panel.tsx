"use client";
interface QuotaStatus { namespace: string; resource: string; used: number; limit: number; pct: number; }
interface ResQuotaEnfPanelProps { quotas: QuotaStatus[]; }
export function ResQuotaEnfPanel({ quotas }: ResQuotaEnfPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Resource Quotas</h3>
        <span className="text-xs text-gray-400">{quotas.length} quotas</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {quotas.map(q => (
          <div key={`${q.namespace}-${q.resource}`} className="px-4 py-1.5 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono">{q.namespace}/{q.resource}</span>
              <span className="text-gray-400">{q.used}/{q.limit} ({q.pct}%)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${q.pct > 90 ? "bg-red-500" : q.pct > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(q.pct, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
