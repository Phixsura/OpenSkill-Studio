"use client";

interface EndpointResult { path: string; method: string; statusCode: number;
  latencyMs: number; healthy: boolean; }
interface EndpointHealthTableProps { results: EndpointResult[]; overall: string;
  healthPct: number; avgLatencyMs: number; }

const METHOD_COLOR: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600",
};

export function EndpointHealthTable({ results, overall, healthPct, avgLatencyMs }: EndpointHealthTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏥 Endpoint Health</h3>
        <div className="flex gap-2 text-xs">
          <span>{healthPct}% healthy</span>
          <span className="text-gray-400">Avg: {avgLatencyMs}ms</span>
          <span className={`px-2 py-0.5 rounded-full ${overall === "healthy" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>{overall}</span>
        </div>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Endpoint</th><th className="p-3">Status</th>
          <th className="p-3">Latency</th><th className="p-3">Health</th>
        </tr></thead>
        <tbody>
          {results.map(r => (
            <tr key={`${r.method}-${r.path}`} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3">
                <span className={`font-bold text-xs mr-1 ${METHOD_COLOR[r.method] || ""}`}>{r.method}</span>
                <span className="font-mono text-xs">{r.path}</span>
              </td>
              <td className={`p-3 text-center ${r.statusCode >= 400 ? "text-red-500" : "text-green-600"}`}>{r.statusCode}</td>
              <td className={`p-3 text-center ${r.latencyMs > 1000 ? "text-red-500" : ""}`}>{r.latencyMs}ms</td>
              <td className="p-3 text-center">{r.healthy ? "✅" : "❌"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
