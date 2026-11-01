"use client";

interface Quota { name: string; used: number; limit: number; pctUsed: number;
  status: string; remaining: number; }
interface RateQuotaDashboardProps { quotas: Quota[]; atRisk: number;
  exhausted: number; healthy: number; }

export function RateQuotaDashboard({ quotas, atRisk, exhausted, healthy }: RateQuotaDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Quota Dashboard</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{healthy} ok</span>
          {atRisk > 0 && <span className="text-yellow-600">{atRisk} at risk</span>}
          {exhausted > 0 && <span className="text-red-500">{exhausted} exhausted</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {quotas.map(q => {
          const color = q.status === "exhausted" ? "bg-red-500" : q.status === "at_risk" ? "bg-yellow-500" : "bg-green-500";
          return (
            <div key={q.name} className="px-4 py-2.5">
              <div className="flex justify-between text-xs mb-0.5">
                <span className="font-medium">{q.name}</span>
                <span className="text-gray-400">{q.used}/{q.limit} ({q.pctUsed}%)</span>
              </div>
              <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(q.pctUsed, 100)}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
