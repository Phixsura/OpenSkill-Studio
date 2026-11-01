"use client";

interface GraphNode { id: string; name: string; icon: string; }
interface GraphEdge { from: string; to: string; }
interface AppDepGraphProps { nodes: GraphNode[]; edges: GraphEdge[];
  roots: string[]; leaves: string[]; }

export function AppDepGraph({ nodes, edges, roots, leaves }: AppDepGraphProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔗 App Dependencies</h3>
      <div className="flex gap-2 mb-3 text-xs text-gray-400">
        <span>{nodes.length} apps</span>
        <span>{edges.length} dependencies</span>
      </div>
      <div className="space-y-2">
        {nodes.map(n => {
          const deps = edges.filter(e => e.from === n.id);
          const isRoot = roots.includes(n.id);
          const isLeaf = leaves.includes(n.id);
          return (
            <div key={n.id} className={`flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2 ${isRoot ? "ring-1 ring-blue-300" : ""}`}>
              <div className="flex items-center gap-2">
                <span>{n.icon}</span>
                <span className="text-sm font-medium">{n.name}</span>
                {isRoot && <span className="text-xs text-blue-500">root</span>}
                {isLeaf && <span className="text-xs text-green-500">leaf</span>}
              </div>
              {deps.length > 0 && (
                <span className="text-xs text-gray-400">→ {deps.map(d => d.to).join(", ")}</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
