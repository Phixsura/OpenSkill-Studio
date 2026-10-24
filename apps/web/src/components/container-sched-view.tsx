"use client";

interface NodeInfo { name: string; cpuPct: number; memPct: number; }
interface ContainerSchedViewProps { nodes: NodeInfo[]; cpuPct: number; memPct: number; }

export function ContainerSchedView({ nodes, cpuPct, memPct }: ContainerSchedViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Container Scheduler</h3>
        <span className="text-xs text-gray-400">CPU {cpuPct}% · MEM {memPct}%</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {nodes.map(n => (
          <div key={n.name} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-1">
              <span className="font-mono">{n.name}</span>
              <span className="text-gray-400">CPU {n.cpuPct}% · MEM {n.memPct}%</span>
            </div>
            <div className="flex gap-1">
              <div className="flex-1 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${n.cpuPct > 80 ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${n.cpuPct}%` }} />
              </div>
              <div className="flex-1 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${n.memPct > 80 ? "bg-red-500" : "bg-purple-500"}`} style={{ width: `${n.memPct}%` }} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
