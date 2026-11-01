"use client";

interface ApiEdge { source: string; target: string; calls: number; avgMs: number; }
interface ApiDepGraphProps { nodes: string[]; edges: ApiEdge[];
  nodeCount: number; totalCalls: number; }

export function ApiDepGraph({ nodes, edges, nodeCount, totalCalls }: ApiDepGraphProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 API Dependency Graph</h3>
        <span className="text-xs text-gray-400">{nodeCount} services · {totalCalls.toLocaleString()} calls</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {edges.map(e => (
          <div key={`${e.source}→${e.target}`} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{e.source} → {e.target}</span>
            <span className="text-gray-400">{e.calls.toLocaleString()} calls · {e.avgMs}ms avg</span>
          </div>
        ))}
      </div>
    </div>
  );
}
