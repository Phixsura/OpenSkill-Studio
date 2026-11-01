"use client";

interface CostCenterViewProps { dimension: string; allocations: Record<string, number>;
  total: number; top: string | null; trend: string; pctChange: number; }

export function CostCenterView({ dimension, allocations, total, top, trend, pctChange }: CostCenterViewProps) {
  const maxVal = Math.max(...Object.values(allocations), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💰 Cost by {dimension}</h3>
        <div className="flex gap-2 text-xs">
          <span className="font-bold">${total.toLocaleString()}</span>
          <span className={trend === "up" ? "text-red-500" : "text-green-600"}>
            {trend === "up" ? "↑" : "↓"}{Math.abs(pctChange)}%
          </span>
        </div>
      </div>
      <div className="p-4 space-y-2">
        {Object.entries(allocations).map(([key, val]) => (
          <div key={key}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className={key === top ? "font-bold" : ""}>{key}</span>
              <span className="text-gray-400">${val.toLocaleString()}</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(val / maxVal) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
