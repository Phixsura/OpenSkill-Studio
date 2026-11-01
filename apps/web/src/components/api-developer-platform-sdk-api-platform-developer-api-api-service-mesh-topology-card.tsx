"use client";

interface NodeInfo { service_id: string; name: string; healthy: boolean; request_rate: number; }
interface EdgeInfo { source: string; target: string; protocol: string; avg_latency_ms: number; }
interface Props { nodes: NodeInfo[]; edges: EdgeInfo[]; unhealthyCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiServiceMeshTopologyCard({ nodes, edges, unhealthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🕸️ Service Mesh</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {nodes.length} services · {edges.length} connections</p>
        </div>
        {unhealthyCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🔴 {unhealthyCount} down</span>}
      </div>
      <div className="space-y-1">
        {nodes.map((n) => (
          <div key={n.service_id} className="flex items-center justify-between text-[11px]">
            <div className="flex items-center gap-1.5">
              <span className={`h-2 w-2 rounded-full ${n.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-gray-700 dark:text-gray-300">{n.name}</span>
            </div>
            <span className="text-gray-400">{n.request_rate} req/s</span>
          </div>
        ))}
      </div>
    </div>
  );
}
