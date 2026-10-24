"use client";

interface ClusterNode { name: string; cpuCores: number; memoryGb: number;
  zone: string; cpuUsedPct: number; memoryUsedPct: number; status: string; }
interface ClusterNodeGridProps { nodes: ClusterNode[]; ready: number;
  pressure: number; totalCpuCores: number; avgCpuPct: number; }

export function ClusterNodeGrid({ nodes, ready, pressure, totalCpuCores, avgCpuPct }: ClusterNodeGridProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🖥️ Cluster Nodes</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{ready} ready</span>
          {pressure > 0 && <span className="text-red-500">{pressure} pressure</span>}
          <span className="text-gray-400">{totalCpuCores} cores · avg {avgCpuPct}%</span>
        </div>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 p-3">
        {nodes.map(n => (
          <div key={n.name} className={`rounded-lg border p-2 ${n.status === "ready" ? "border-green-300 dark:border-green-800" : "border-red-300 dark:border-red-800"}`}>
            <div className="text-xs font-mono font-bold">{n.name}</div>
            <div className="text-[10px] text-gray-400">{n.zone} · {n.cpuCores}C/{n.memoryGb}G</div>
            <div className="flex gap-2 mt-1 text-[10px]">
              <span>CPU {n.cpuUsedPct}%</span>
              <span>Mem {n.memoryUsedPct}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
