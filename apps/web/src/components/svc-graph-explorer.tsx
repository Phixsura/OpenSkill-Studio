"use client";

interface GraphNode { id: string; type: string; team: string; healthy: boolean; }
interface SvcGraphExplorerProps { nodes: GraphNode[]; nodeCount: number;
  edgeCount: number; healthy: number; teams: string[]; }

export function SvcGraphExplorer({ nodes, nodeCount, edgeCount, healthy, teams }: SvcGraphExplorerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗺️ Service Graph</h3>
        <span className="text-xs text-gray-400">{nodeCount} services · {edgeCount} deps · {teams.length} teams</span>
      </div>
      <div className="grid grid-cols-3 sm:grid-cols-4 gap-2 p-3">
        {nodes.map(n => (
          <div key={n.id} className={`rounded-lg border p-2 text-center text-xs ${n.healthy ? "border-green-300" : "border-red-300"}`}>
            <div className="font-mono font-bold">{n.id}</div>
            <div className="text-[10px] text-gray-400">{n.team}</div>
          </div>
        ))}
      </div>
      <div className="px-4 py-2 border-t dark:border-gray-700 text-[10px] text-gray-400">
        {healthy}/{nodeCount} healthy · Teams: {teams.join(", ")}
      </div>
    </div>
  );
}
