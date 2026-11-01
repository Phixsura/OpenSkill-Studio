"use client";

interface EndpointHealth { path: string; method: string; p99Ms: number;
  errorRate: number; rpm: number; status: string; }
interface EndpointHealthGridProps { endpoints: EndpointHealth[]; healthPct: number;
  healthy: number; degraded: number; unhealthy: number; }

const STATUS_DOTS: Record<string, string> = {
  healthy: "bg-green-500", degraded: "bg-yellow-500", unhealthy: "bg-red-500",
};
const METHOD_COLORS: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600",
};

export function EndpointHealthGrid({ endpoints, healthPct, healthy, degraded, unhealthy }: EndpointHealthGridProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏥 Endpoint Health</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{healthy}✓</span>
          {degraded > 0 && <span className="text-yellow-600">{degraded}~</span>}
          {unhealthy > 0 && <span className="text-red-500">{unhealthy}✗</span>}
          <span className="text-gray-400">{healthPct}%</span>
        </div>
      </div>
      <table className="w-full text-xs">
        <thead><tr className="text-gray-400 border-b dark:border-gray-700">
          <th className="p-2 text-left">Endpoint</th>
          <th className="p-2 text-right">P99</th>
          <th className="p-2 text-right">Errors</th>
          <th className="p-2 text-right">RPM</th>
          <th className="p-2 text-center">Status</th>
        </tr></thead>
        <tbody>
          {endpoints.map(ep => (
            <tr key={`${ep.method}${ep.path}`} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-2"><span className={`font-mono ${METHOD_COLORS[ep.method] ?? ""}`}>{ep.method}</span> {ep.path}</td>
              <td className="p-2 text-right">{ep.p99Ms}ms</td>
              <td className="p-2 text-right">{ep.errorRate}%</td>
              <td className="p-2 text-right">{ep.rpm}</td>
              <td className="p-2 text-center"><span className={`inline-block w-2 h-2 rounded-full ${STATUS_DOTS[ep.status] ?? ""}`} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
