"use client";

interface Resource { name: string; used: number; limit: number; pct: number; status: string; unit: string; }
interface UsageQuotaProps { resources: Resource[]; }

const statusColors: Record<string, string> = {
  ok: "bg-green-500",
  warning: "bg-yellow-500",
  critical: "bg-red-500",
};

export function UsageQuota({ resources }: UsageQuotaProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Usage & Quotas</h3>
      {resources.map(r => (
        <div key={r.name} className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">{r.name}</span>
            <span className="text-xs text-gray-400">{r.used.toLocaleString()} / {r.limit.toLocaleString()} {r.unit}</span>
          </div>
          <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className={`h-full rounded-full transition-all ${statusColors[r.status] ?? "bg-gray-400"}`}
              style={{ width: `${Math.min(r.pct, 100)}%` }} />
          </div>
          {r.status === "critical" && <p className="text-xs text-red-500">⚠ Approaching limit ({r.pct}%)</p>}
        </div>
      ))}
    </div>
  );
}
