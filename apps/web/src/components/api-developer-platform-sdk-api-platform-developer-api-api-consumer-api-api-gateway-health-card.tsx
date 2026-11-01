"use client";

interface NodeInfo { node_id: string; region: string; healthy: boolean; rps: number; error_rate: number; }
interface Props { nodes: NodeInfo[]; unhealthyCount: number; totalRps: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiGatewayHealthCard({ nodes, unhealthyCount, totalRps, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 Gateway Health</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalRps} rps total</p>
        </div>
        {unhealthyCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🔴 {unhealthyCount} down</span>}
      </div>
      {nodes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No gateway nodes</p>
      ) : (
        <div className="space-y-1">
          {nodes.map((n) => (
            <div key={n.node_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${n.healthy ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{n.region}</span>
              </div>
              <span className="text-gray-400">{n.rps} rps</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
