"use client";
interface NodeInfo { name: string; role: string; cpu: number; memoryGb: number; status: string; cordoned: boolean; }
interface ClusterNodePanelProps { nodes: NodeInfo[]; totalCpu: number; totalMemGb: number; ready: number; }
export function ClusterNodePanel({ nodes, totalCpu, totalMemGb, ready }: ClusterNodePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🖥️ Cluster Nodes</h3>
        <span className="text-xs text-gray-400">{ready}/{nodes.length} ready · {totalCpu} CPU · {totalMemGb}GB</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {nodes.map(n => (
          <div key={n.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${n.status === "ready" ? "bg-green-500" : "bg-yellow-500"}`} />
              <span className="font-mono">{n.name}</span>
              <span className="text-gray-400">{n.role}</span>
            </div>
            <span className="text-gray-400">{n.cpu}CPU · {n.memoryGb}GB{n.cordoned ? " · 🚧" : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
