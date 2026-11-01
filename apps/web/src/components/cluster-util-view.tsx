"use client";

interface ClusterUtilViewProps { clusterCount: number; cpuPct: number; memPct: number;
  cpuCapacity: number; cpuUsed: number; memCapacityGb: number; memUsedGb: number;
  overallHealth: string; }

export function ClusterUtilView({ clusterCount, cpuPct, memPct, cpuCapacity, cpuUsed, memCapacityGb, memUsedGb, overallHealth }: ClusterUtilViewProps) {
  const color = (pct: number) => pct > 85 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🖥️ Cluster Utilization</h3>
        <span className={`text-xs ${overallHealth === "healthy" ? "text-green-600" : "text-yellow-600"}`}>
          {clusterCount} clusters · {overallHealth}
        </span>
      </div>
      <div className="p-4 space-y-3">
        <div>
          <div className="flex justify-between text-xs mb-0.5">
            <span>CPU</span><span>{cpuUsed}/{cpuCapacity} cores ({cpuPct}%)</span>
          </div>
          <div className="w-full h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full">
            <div className={`h-full rounded-full ${color(cpuPct)}`} style={{ width: `${cpuPct}%` }} />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-xs mb-0.5">
            <span>Memory</span><span>{memUsedGb}/{memCapacityGb} GB ({memPct}%)</span>
          </div>
          <div className="w-full h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full">
            <div className={`h-full rounded-full ${color(memPct)}`} style={{ width: `${memPct}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
}
