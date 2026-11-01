"use client";

interface Allocation { app_id: string; cost_cents: number; pct: number; }
interface CostAllocationChartProps { allocations: Allocation[]; totalCents: number; period: string; }

const COLORS = ["bg-blue-500", "bg-green-500", "bg-yellow-500", "bg-purple-500", "bg-red-500", "bg-indigo-500"];

export function CostAllocationChart({ allocations, totalCents, period }: CostAllocationChartProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Cost Allocation</h3>
        <div className="text-right">
          <p className="text-lg font-bold">${(totalCents / 100).toFixed(2)}</p>
          <p className="text-xs text-gray-400">{period}</p>
        </div>
      </div>
      <div className="mt-3 flex h-4 overflow-hidden rounded-full">
        {allocations.map((a, i) => (
          <div key={a.app_id} className={`${COLORS[i % COLORS.length]}`} style={{ width: `${a.pct}%` }}
            title={`${a.app_id}: ${a.pct}%`} />
        ))}
      </div>
      <ul className="mt-3 space-y-1">
        {allocations.slice(0, 5).map((a, i) => (
          <li key={a.app_id} className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-1">
              <span className={`h-2 w-2 rounded-full ${COLORS[i % COLORS.length]}`} />
              {a.app_id}
            </span>
            <span className="text-gray-400">${(a.cost_cents / 100).toFixed(2)} ({a.pct}%)</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
