"use client";

interface EndpointPerf { endpoint: string; total: number; avgMs: number;
  p50Ms: number; p99Ms: number; errorRate: number; health: string; }
interface EndpointPerfTableProps { endpoints: EndpointPerf[]; totalRequests: number; }

const HEALTH_BADGE: Record<string, string> = {
  good: "bg-green-100 text-green-700", ok: "bg-yellow-100 text-yellow-700", poor: "bg-red-100 text-red-700",
};

export function EndpointPerfTable({ endpoints, totalRequests }: EndpointPerfTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Endpoint Performance</h3>
        <span className="text-xs text-gray-400">{totalRequests.toLocaleString()} requests</span>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Endpoint</th><th className="p-3">Avg</th>
          <th className="p-3">P50</th><th className="p-3">P99</th>
          <th className="p-3">Errors</th><th className="p-3">Health</th>
        </tr></thead>
        <tbody>
          {endpoints.map(e => (
            <tr key={e.endpoint} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 font-mono text-xs">{e.endpoint}</td>
              <td className="p-3 text-center text-xs">{e.avgMs}ms</td>
              <td className="p-3 text-center text-xs">{e.p50Ms}ms</td>
              <td className="p-3 text-center text-xs">{e.p99Ms}ms</td>
              <td className="p-3 text-center text-xs">{e.errorRate}%</td>
              <td className="p-3 text-center">
                <span className={`text-xs px-1.5 py-0.5 rounded ${HEALTH_BADGE[e.health] || ""}`}>{e.health}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
