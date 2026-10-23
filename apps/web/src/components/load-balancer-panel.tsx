"use client";

interface BackendInfo { id: string; healthy: boolean; rps: number; latencyMs: number; }
interface LoadBalancerPanelProps { status: string; totalRps: number; avgLatencyMs: number;
  backends: BackendInfo[]; healthyCount: number; unhealthyCount: number; }

export function LoadBalancerPanel({ status, totalRps, avgLatencyMs, backends, healthyCount, unhealthyCount }: LoadBalancerPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">⚖️ Load Balancer</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          status === "healthy" ? "bg-green-100 text-green-700" :
          status === "degraded" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
        }`}>{status}</span>
      </div>
      <div className="grid grid-cols-3 gap-3 mb-4 text-center">
        <div><p className="text-lg font-bold">{totalRps.toLocaleString()}</p><p className="text-xs text-gray-400">Total RPS</p></div>
        <div><p className="text-lg font-bold">{avgLatencyMs}ms</p><p className="text-xs text-gray-400">Avg Latency</p></div>
        <div>
          <p className="text-lg font-bold">{healthyCount}<span className="text-gray-300">/{healthyCount + unhealthyCount}</span></p>
          <p className="text-xs text-gray-400">Healthy</p>
        </div>
      </div>
      <div className="space-y-2">
        {backends.map(b => (
          <div key={b.id} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2 text-sm">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${b.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono text-xs">{b.id}</span>
            </div>
            <div className="flex gap-4 text-xs text-gray-400">
              <span>{b.rps} rps</span>
              <span>{b.latencyMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
