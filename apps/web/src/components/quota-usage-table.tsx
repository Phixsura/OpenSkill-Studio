"use client";

interface QuotaItem { resource: string; used: number; limit: number; pct: number; warning: boolean; exceeded: boolean; }

interface QuotaUsageTableProps { items: QuotaItem[]; }

export function QuotaUsageTable({ items }: QuotaUsageTableProps) {
  return (
    <div className="space-y-3">
      {items.map(i => (
        <div key={i.resource}>
          <div className="flex justify-between text-sm">
            <span className="capitalize">{i.resource.replace(/_/g, " ")}</span>
            <span className={i.exceeded ? "text-red-600 font-medium" : i.warning ? "text-yellow-600" : "text-gray-500"}>{i.used}/{i.limit}</span>
          </div>
          <div className="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className={`h-2 rounded-full ${i.exceeded ? "bg-red-500" : i.warning ? "bg-yellow-500" : "bg-green-500"}`}
              style={{ width: `${Math.min(i.pct, 100)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
