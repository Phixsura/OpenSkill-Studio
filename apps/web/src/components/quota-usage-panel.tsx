"use client";

interface QuotaItem { resource: string; usage: number; hard: number; soft: number;
  pct: number; unit: string; status: string; }
interface QuotaUsagePanelProps { quotas: QuotaItem[]; }

export function QuotaUsagePanel({ quotas }: QuotaUsagePanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">📏 Quotas</h3>
      <div className="space-y-3">
        {quotas.map(q => (
          <div key={q.resource}>
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium capitalize">{q.resource.replace("_", " ")}</span>
              <span className={q.status === "exceeded" ? "text-red-600" : q.status === "warning" ? "text-yellow-600" : "text-gray-400"}>
                {q.usage.toLocaleString()} / {q.hard.toLocaleString()} {q.unit}
              </span>
            </div>
            <div className="h-2.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all ${
                q.status === "exceeded" ? "bg-red-500" : q.status === "warning" ? "bg-yellow-500" : "bg-green-500"
              }`} style={{ width: `${Math.min(q.pct, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
