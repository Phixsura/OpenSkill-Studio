"use client";

interface Quota { resource: string; used: number; limit: number; unit: string; }

function pct(q: Quota) { return q.limit === 0 ? 0 : Math.min(100, Math.round(q.used / q.limit * 100)); }
function barColor(p: number) { return p >= 90 ? "bg-red-500" : p >= 70 ? "bg-yellow-500" : "bg-blue-500"; }

export function UsageQuotaDashboard({ quotas }: { quotas: Quota[] }) {
  if (!quotas.length) return <div className="text-center text-gray-400 py-6 text-sm">No quotas configured</div>;
  return (
    <div className="space-y-3">
      {quotas.map((q) => {
        const p = pct(q);
        return (
          <div key={q.resource} className="border dark:border-gray-700 rounded-xl p-3">
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium">{q.resource}</span>
              <span className="text-xs text-gray-500">
                {q.used.toLocaleString()} / {q.limit === 0 ? "∞" : q.limit.toLocaleString()} {q.unit}
              </span>
            </div>
            <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all ${barColor(p)}`} style={{ width: `${p}%` }} />
            </div>
            {p >= 90 && <span className="text-xs text-red-500 mt-1 block">⚠️ Approaching limit</span>}
          </div>
        );
      })}
    </div>
  );
}
