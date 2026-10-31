"use client";

interface DepNode { name: string; version: string; size_kb: number; dep_count: number; }
interface DepEdge { from: string; to: string; }
interface DependencyGraphProps { nodes: DepNode[]; edges: DepEdge[]; totalSizeKb: number; maxDepth: number; }

export function DependencyGraph({ nodes, edges, totalSizeKb, maxDepth }: DependencyGraphProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Dependencies</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{nodes.length} packages</span>
          <span>{(totalSizeKb / 1024).toFixed(1)} MB</span>
          <span>depth {maxDepth}</span>
        </div>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {nodes.map(n => (
          <div key={n.name} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
            <div>
              <p className="text-sm font-medium font-mono">{n.name}</p>
              <p className="text-xs text-gray-400">v{n.version} · {n.dep_count} deps</p>
            </div>
            <span className="text-xs text-gray-500">{n.size_kb} KB</span>
          </div>
        ))}
      </div>
    </div>
  );
}
