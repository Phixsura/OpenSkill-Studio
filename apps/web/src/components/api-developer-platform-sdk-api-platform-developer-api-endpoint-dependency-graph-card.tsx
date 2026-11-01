"use client";

interface DepNode { endpoint_id: string; method: string; path: string; dep_count: number; dependent_count: number; }
interface Props { nodes: DepNode[]; cycleCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDependencyGraphCard({ nodes, cycleCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Endpoint Dependencies</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {nodes.length} endpoints</p>
        </div>
        {cycleCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⚠️ {cycleCount} cycles</span>}
      </div>
      {nodes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints mapped</p>
      ) : (
        <div className="space-y-1">
          {nodes.map((n) => (
            <div key={n.endpoint_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="rounded bg-blue-100 px-1 font-mono text-[9px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{n.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{n.path}</span>
              </div>
              <span className="text-gray-400">↗{n.dep_count} ↙{n.dependent_count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
