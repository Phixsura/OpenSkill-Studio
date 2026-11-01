"use client";

interface Forecast { month: number; projected: number; }
interface CapacityPlannerCardProps { currentUsage: number; forecasts: Forecast[]; recommendedPlan: string; shouldScale: boolean; }

export function CapacityPlannerCard({ currentUsage, forecasts, recommendedPlan, shouldScale }: CapacityPlannerCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Capacity Planning</h3>
        {shouldScale && <span className="rounded bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700">⚠️ Scale recommended</span>}
      </div>
      <p className="mt-1 text-sm text-gray-500">Current: {currentUsage.toLocaleString()} calls/mo</p>
      <div className="mt-3">
        <p className="text-xs font-medium text-gray-500">Forecast</p>
        <div className="mt-1 flex gap-4">
          {forecasts.slice(0, 3).map(f => (
            <div key={f.month} className="text-center">
              <p className="text-sm font-bold">{f.projected.toLocaleString()}</p>
              <p className="text-xs text-gray-400">+{f.month}mo</p>
            </div>
          ))}
        </div>
      </div>
      <p className="mt-3 text-xs">💡 Recommended: <span className="font-semibold">{recommendedPlan}</span></p>
    </div>
  );
}
