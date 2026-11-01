"use client";

interface Node { path: string; incoming: number; outgoing: number; isRoot: boolean; isLeaf: boolean; }
interface Edge { from: string; to: string; callCount: number; avgMs: number; }
interface Props { nodes: Node[]; edges: Edge[]; maxDepth: number; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiEndpointDependencyGraphCard({ nodes, edges, maxDepth, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🕸️ Dependency Graph</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {nodes.length} endpoints · Depth: {maxDepth}</p>
      </div>
      {edges.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No dependencies</p>
      ) : (
        <div className="space-y-1">
          {edges.map((e, i) => (
            <div key={i} className="flex items-center gap-1 rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <code className="text-gray-600 dark:text-gray-400">{e.from}</code>
              <span className="text-gray-400">→</span>
              <code className="text-blue-600 dark:text-blue-400">{e.to}</code>
              <span className="ml-auto text-gray-400">{e.callCount} calls · {e.avgMs}ms</span>
            </div>
          ))}
        </div>
      )}
      {nodes.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {nodes.filter(n => n.isRoot).map(n => <span key={n.path} className="rounded bg-green-100 px-1 py-0.5 text-[8px] text-green-700 dark:bg-green-900/30 dark:text-green-400">root: {n.path}</span>)}
          {nodes.filter(n => n.isLeaf).map(n => <span key={n.path} className="rounded bg-amber-100 px-1 py-0.5 text-[8px] text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">leaf: {n.path}</span>)}
        </div>
      )}
    </div>
  );
}
