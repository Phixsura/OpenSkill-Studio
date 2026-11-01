"use client";
interface Node { name: string; health: string; }
interface Edge { source: string; destination: string; edgeHealth: string; latencyMs: number; }
interface MapHealthPanelProps { nodes: Node[]; edges: Edge[]; healthyNodes: number; totalNodes: number; }
const DOT: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", down: "bg-red-500" };
export function MapHealthPanel({ nodes, edges, healthyNodes, totalNodes }: MapHealthPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗺️ Service Map Health</h3>
        <span className="text-xs text-gray-400">{healthyNodes}/{totalNodes} healthy</span>
      </div>
      <div className="p-4 flex flex-wrap gap-2 mb-2">
        {nodes.map(n => (
          <div key={n.name} className="flex items-center gap-1 text-xs">
            <span className={`w-2.5 h-2.5 rounded-full ${DOT[n.health] ?? "bg-gray-400"}`} />
            <span>{n.name}</span>
          </div>
        ))}
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {edges.map(e => (
          <div key={`${e.source}→${e.destination}`} className="flex justify-between px-4 py-1 text-xs">
            <span className="font-mono">{e.source} → {e.destination}</span>
            <span className={e.edgeHealth === "healthy" ? "text-green-600" : "text-yellow-600"}>
              {e.edgeHealth} · {e.latencyMs}ms
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
