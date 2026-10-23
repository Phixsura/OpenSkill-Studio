"use client";

interface GraphNode { id: string; in: number; out: number; }
interface GraphEdge { source: string; target: string; type: string; }
interface DepGraphViewProps { nodes: GraphNode[]; edges: GraphEdge[];
  roots: string[]; leaves: string[]; }

export function DepGraphView({ nodes, edges, roots, leaves }: DepGraphViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🕸️ Dependency Graph</h3>
        <span className="text-xs text-gray-400">{nodes.length} nodes · {edges.length} edges</span>
      </div>
      <div className="p-4 grid grid-cols-2 gap-4">
        <div>
          <div className="text-xs text-gray-400 mb-2">Entry Points</div>
          {roots.map(r => (
            <span key={r} className="inline-block mr-1 mb-1 px-2 py-0.5 text-xs bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded font-mono">{r}</span>
          ))}
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-2">Leaf Dependencies</div>
          {leaves.map(l => (
            <span key={l} className="inline-block mr-1 mb-1 px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded font-mono">{l}</span>
          ))}
        </div>
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {edges.map((e, i) => (
          <div key={i} className="flex items-center gap-2 px-4 py-1.5 text-xs">
            <span className="font-mono">{e.source}</span>
            <span className="text-gray-400">→</span>
            <span className="font-mono">{e.target}</span>
            <span className="text-gray-400 ml-auto">{e.type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
