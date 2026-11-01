"use client";

interface HealthBeaconPanelProps { uniqueServices: number; healthyPct: number;
  allHealthy: boolean; byStatus: Record<string, number>; staleServices: string[]; }

export function HealthBeaconPanel({ uniqueServices, healthyPct, allHealthy, byStatus, staleServices }: HealthBeaconPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💓 Health Beacons</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{uniqueServices} services</span>
          <span className={allHealthy ? "text-green-600" : "text-yellow-600"}>
            {allHealthy ? "✅ All Healthy" : `${healthyPct}% healthy`}
          </span>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {Object.entries(byStatus).map(([status, count]) => (
          <div key={status} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{count}</div>
            <div className="text-[10px] text-gray-400 capitalize">{status}</div>
          </div>
        ))}
      </div>
      {staleServices.length > 0 && (
        <div className="p-3 bg-yellow-50 dark:bg-yellow-900/10">
          <div className="text-xs text-yellow-700">⚠ Stale: {staleServices.join(", ")}</div>
        </div>
      )}
    </div>
  );
}
