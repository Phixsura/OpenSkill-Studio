"use client";

interface EndpointHealth { endpoint: string; status: string; successRate: number; avgMs: number; total: number; }

interface EndpointHealthTableProps { endpoints: EndpointHealth[]; }

const STATUS_STYLES: Record<string, string> = {
  healthy: "text-green-600", degraded: "text-yellow-600", unhealthy: "text-red-600", unknown: "text-gray-400",
};

export function EndpointHealthTable({ endpoints }: EndpointHealthTableProps) {
  if (endpoints.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No endpoint data</p>;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead><tr className="border-b dark:border-gray-700">
          <th className="px-3 py-2">Endpoint</th><th className="px-3 py-2">Status</th>
          <th className="px-3 py-2">Success</th><th className="px-3 py-2">Avg Latency</th><th className="px-3 py-2">Total</th>
        </tr></thead>
        <tbody>{endpoints.map(ep => (
          <tr key={ep.endpoint} className="border-b dark:border-gray-800">
            <td className="max-w-[200px] truncate px-3 py-2 font-mono text-xs">{ep.endpoint}</td>
            <td className={`px-3 py-2 font-medium capitalize ${STATUS_STYLES[ep.status] ?? ""}`}>{ep.status}</td>
            <td className="px-3 py-2">{ep.successRate}%</td>
            <td className="px-3 py-2">{ep.avgMs}ms</td>
            <td className="px-3 py-2">{ep.total}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  );
}
