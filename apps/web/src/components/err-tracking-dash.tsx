"use client";

interface ErrorGroup { type: string; count: number; services: string[]; serviceCount: number; }
interface ErrTrackingDashProps { errors: ErrorGroup[]; totalErrors: number;
  uniqueTypes: number; topError: string | null; trend: string; pctChange: number; }

export function ErrTrackingDash({ errors, totalErrors, uniqueTypes, topError, trend, pctChange }: ErrTrackingDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐛 Error Tracking</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{totalErrors} errors · {uniqueTypes} types</span>
          <span className={trend === "decreasing" ? "text-green-600" : "text-red-500"}>
            {trend === "decreasing" ? "↓" : "↑"}{Math.abs(pctChange)}%
          </span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {errors.map(e => (
          <div key={e.type} className="px-4 py-2.5">
            <div className="flex justify-between text-xs">
              <span className="font-mono text-red-600">{e.type}</span>
              <span className="text-gray-400">{e.count}× · {e.serviceCount} services</span>
            </div>
            <div className="text-[10px] text-gray-400 mt-0.5">{e.services.join(", ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
